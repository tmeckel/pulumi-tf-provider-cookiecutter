//go:build exclude

package main

import (
	"bufio"
	"errors"
	"fmt"
	"go/ast"
	"go/parser"
	"go/printer"
	"go/token"
	"log"
	"os"
	"os/exec"
	"reflect"
	"regexp"
	"strings"
)

var (
	rxMissingResource   = regexp.MustCompile(`TF resource "(\w+)" not`)
	rxMissingDataSource = regexp.MustCompile(`TF data source "(\w+)" not`)
)

// addNewline is a hack to let us force a newline at a certain position. (https://github.com/mvdan/gofumpt/blob/master/format/format.go#L217)
func addNewline(f *token.File, at token.Pos) {
	offset := f.Offset(at)

	field := reflect.ValueOf(f).Elem().FieldByName("lines")
	n := field.Len()
	lines := make([]int, 0, n+1)
	for i := 0; i < n; i++ {
		cur := int(field.Index(i).Int())
		if offset == cur {
			// This newline already exists; do nothing. Duplicate
			// newlines can't exist.
			return
		}
		if offset >= 0 && offset < cur {
			lines = append(lines, offset)
			offset = -1
		}
		lines = append(lines, cur)
	}
	if offset >= 0 {
		lines = append(lines, offset)
	}
	if !f.SetLines(lines) {
		panic(fmt.Sprintf("could not set lines to %v", lines))
	}
}

func addKeyToMap(name, fnc string, pos token.Pos, kve *ast.KeyValueExpr) {
	resExpr := ast.KeyValueExpr{
		Key: &ast.BasicLit{
			Kind:     token.STRING,
			Value:    fmt.Sprintf("%q", name),
			ValuePos: pos,
		},
		Value: &ast.CompositeLit{
			Elts: []ast.Expr{
				&ast.KeyValueExpr{
					Key: ast.NewIdent("Tok"),
					Value: &ast.CallExpr{
						Fun: ast.NewIdent(fnc),
						Args: []ast.Expr{
							ast.NewIdent("mainMod"),
							&ast.BasicLit{
								Kind:  token.STRING,
								Value: fmt.Sprintf("%q", name),
							},
						},
					},
				},
			},
		},
	}
	kve.Value.(*ast.CompositeLit).Elts = append(kve.Value.(*ast.CompositeLit).Elts, &resExpr)
}

func main() {
	fmt.Println("🧱 Building tfgen ...")
	cmd := exec.Command("make", "-C", "..", "tfgen")
	cmd.Env = os.Environ()
	cmd.Env = append(cmd.Env, "PULUMI_SKIP_MISSING_MAPPING_ERROR=1")

	r, _ := cmd.StderrPipe()
	done := make(chan struct{})
	scanner := bufio.NewScanner(r)

	stderr := []string{}
	missingResources := []string{}
	missingDataSources := []string{}

	go func() {
		// Read line by line and process it
		for scanner.Scan() {
			line := scanner.Text()
			stderr = append(stderr, line)

			for i, m := range rxMissingResource.FindStringSubmatch(line) {
				if i > 0 { // ignore initial match because it contains the complete line if the regex matches
					fmt.Printf("✨ Missing resource %s\n", m)
					missingResources = append(missingResources, m)
				}
			}

			for i, m := range rxMissingDataSource.FindStringSubmatch(line) {
				if i > 0 { // ignore initial match because it contains the complete line if the regex matches
					fmt.Printf("✨ Missing data source %s\n", m)
					missingDataSources = append(missingDataSources, m)
				}
			}

		}

		// We're all done, unblock the channel
		done <- struct{}{}
	}()

	// Start the command and check for errors
	err := cmd.Start()
	if err != nil {
		log.Fatalf("failed to start cmd: error(%T): %s", err, err)
	}

	// Wait for all output to be processed
	<-done

	// Wait for the command to finish
	err = cmd.Wait()
	if execErr := (&exec.ExitError{}); errors.As(err, &execErr) {
		if execErr.ExitCode() != 2 {
			log.Fatalf("🔥 Failed build tfgen failed with error(%T): %s", err, err)
		} else if len(missingResources) == 0 && len(missingDataSources) == 0 {
			log.Fatalf("🔥 Failed build tfgen with error(%T): %s\n", err, err, strings.Join(stderr, "\n"))
		}
	} else if err != nil {
		log.Fatalf("🔥 Failed build tfgen with error(%T): %s", err, err)
	}

	if len(missingResources) == 0 && len(missingDataSources) == 0 {
		fmt.Println("🌈 No missing resources or data sources found")
		return
	}

	srcFile := "resources.go"
	fset := token.NewFileSet()
	f, err := parser.ParseFile(fset, srcFile, nil, parser.ParseComments|parser.SkipObjectResolution)
	if err != nil {
		log.Fatal(err)
	}

	var providerDecl *ast.CompositeLit
	ast.Inspect(f, func(n ast.Node) bool {
		switch x := n.(type) {
		case *ast.AssignStmt:
			if c, ok := x.Rhs[0].(*ast.CompositeLit); ok {
				s, ok := c.Type.(*ast.SelectorExpr)
				if ok && s.Sel.Name == "ProviderInfo" {
					providerDecl = c
					return false
				}
			}
		}
		return true
	})

	if providerDecl != nil {
		fmt.Println("🎯 Adding missing resources and data sources ...")
		for _, e := range providerDecl.Elts {
			kve, ok := e.(*ast.KeyValueExpr)
			if ok {
				iterateItems := func(items []string) {
					n := kve.Key.(*ast.Ident).Name
					funcName := "make" + n[:len(n)-1]

					var offset token.Pos
					l := len(kve.Value.(*ast.CompositeLit).Elts)
					if l == 0 {
						offset = kve.Value.(*ast.CompositeLit).Rbrace - 7
					} else {
						offset = kve.Value.(*ast.CompositeLit).Elts[l-1].End()
					}
					f := fset.File(kve.Value.(*ast.CompositeLit).Rbrace - 7)
					for i, r := range items {
						pos := token.Pos(int(offset) + i)
						addKeyToMap(r, funcName, pos, kve)
						addNewline(f, pos)
					}
				}
				switch kve.Key.(*ast.Ident).Name {
				case "DataSources":
					iterateItems(missingDataSources)
				case "Resources":
					iterateItems(missingResources)
				}
			}
		}
		io, err := os.Create(srcFile)
		if err != nil {
			log.Fatalf("🔥 Failed to open source file %s", err)
		}
		defer io.Close()

		w := bufio.NewWriter(io)
		err = printer.Fprint(w, fset, f)
		if err != nil {
			log.Fatal(err)
		}
		w.Flush()

		fmt.Println("🚀 Formatting code ...")
		cmd := exec.Command("go", "fmt", srcFile)
		if err := cmd.Run(); err != nil {
			log.Fatal("🔥 Failed formatting code with error(%T): %s", err, err)
		}
	} else {
		log.Fatal("🔥 ProviderInfo declaration not found")
	}
}
