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

func (col *RCollection) GetURLs() []string {
	urls := make([]string, 0, len(col.Requests))
	for _, req := range col.Requests {
		urls = append(urls, req.URL)
	}
	return urls
}
func (col *RCollection) MapURLsToAliases(urls []string) map[string]string {
	aliasMap := make(map[string]string)

	// Build a lookup table for URL -> Alias from the collection.
	lookup := make(map[string]string)
	for _, req := range col.Requests {
		lookup[req.URL] = req.Alias
	}

	// For each URL in the provided slice, check if an alias exists.
	for _, url := range urls {
		if alias, ok := lookup[url]; ok {
			aliasMap[url] = alias
		}
	}

	return aliasMap
}
func (col *RCollection) GetAliasByURL(url string) string {
	for _, req := range col.Requests {
		if req.URL == url {
			return req.Alias
		}
	}
	return ""
}
func (col *RCollection) FindRequests(file, dir, match_type string) error {
	files_to_search := matchFiles(file, dir, match_type)
	fmt.Printf("\nFiles to search: %v\n", files_to_search)
	for _, filePath := range files_to_search {
		var wrapper TargetsWrapper

		f, err := os.Open(filePath)
		if err != nil {
			fmt.Printf("Error when opening %s, reason: %v. Skipping.\n", filePath, err)

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
	fmt.Printf("\n Matching with match_type = %s...\n", match_type)
	basename := filepath.Base(file)
	pure_given_filename_to_compare := strings.TrimSuffix(basename, "-reqmsg-url-alias.json")
	fmt.Printf("\n Trying to match: %s\n", pure_given_filename_to_compare)
	for _, filename := range files_to_match {
		is_appendable := false

		if is_loose {
			if strings.Contains(filename, pure_given_filename_to_compare) {
				fmt.Printf("\nFound %s contains %s", filename, pure_given_filename_to_compare)
				is_appendable = true
			}
		} else {
			potential_matching_basename := filepath.Base(filename)
			pure_potential_matching_basename := strings.TrimSuffix(potential_matching_basename, "-reqmsg-url-alias.json")
			if pure_potential_matching_basename == pure_given_filename_to_compare || potential_matching_basename == basename {
				is_appendable = true
				fmt.Printf("\nFound %s matches %s", filename, file)
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
