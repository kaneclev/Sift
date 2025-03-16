package ipc

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
)

type RequestEncoding struct {
	URL   string `json:"url"`
	Alias string `json:"alias"`
}
type RCollection struct {
	Requests []RequestEncoding
}
type TargetsWrapper struct {
	Targets []RequestEncoding `json:"targets"`
}

func (col *RCollection) FindRequests(file, dir, match_type string) error {
	files_to_search := matchFiles(file, dir, match_type)

	for _, filePath := range files_to_search {
		var wrapper TargetsWrapper

		f, err := os.Open(filePath)
		if err != nil {
			return err
		}

		// Read the file data.
		data, err := io.ReadAll(f)
		f.Close() // Close the file as soon as reading is complete.
		if err != nil {
			fmt.Printf("Error when reading %s, reason: %v. Skipping.\n", filePath, err)
			continue
		}

		// Unmarshal the JSON into the wrapper struct.
		err = json.Unmarshal(data, &wrapper)
		if err != nil {
			fmt.Printf("Error when interpreting %s's JSON, reason: %v. Skipping.\n", filePath, err)
			continue
		}

		// Append the targets from the wrapper to the collection.
		col.Requests = append(col.Requests, wrapper.Targets...)
	}

	return nil
}

func matchFiles(file, dir string, match_type string) []string {
	var valid_files []string
	files_to_match := collectFilenames(dir)
	is_loose := true
	if match_type == "strict" {
		is_loose = false
	}
	basename := filepath.Base(file)
	to_compare := strings.TrimSuffix("-reqmsg-url-alias.json", basename)
	for _, filename := range files_to_match {
		is_appendable := false

		if is_loose {
			if strings.Contains(filename, to_compare) {
				is_appendable = true
			}
		} else {
			if filename == to_compare || filename == basename {
				is_appendable = true
			}
		}
		if is_appendable {
			valid_files = append(valid_files, filename)
		}
	}
	return valid_files

}
func collectFilenames(dir string) []string {
	var files []string

	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		// If there's an error accessing the path, report it and continue.
		if err != nil {
			return err
		}
		// If it's not a directory, add the file path to the list.
		if !info.IsDir() {
			files = append(files, path)
		}
		return nil
	})
	if err != nil {
		fmt.Printf("\nError walking the path %q: %v\n", dir, err)
		return nil
	}
	return files
}
