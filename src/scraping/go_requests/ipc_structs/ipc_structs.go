package ipc_structs

import (
	"encoding/json"
	"fmt"
)

type RequestProperties struct {
	URL   string `json:"url"`
	Alias string `json:"alias"`
}
type Targets struct {
	Targets       []RequestProperties `json:"targets"`
	CorrelationID string              `json:"id"`
}

func (col *Targets) GetURLs() []string {
	urls := make([]string, 0, len(col.Targets))
	for _, req := range col.Targets {
		urls = append(urls, req.URL)
	}
	return urls
}
func (col *Targets) MapURLsToAliases(urls []string) map[string]string {
	aliasMap := make(map[string]string)

	// Build a lookup table for URL -> Alias from the collection.
	lookup := make(map[string]string)
	for _, req := range col.Targets {
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
func (col *Targets) GetAliasByURL(url string) string {
	for _, req := range col.Targets {
		if req.URL == url {
			return req.Alias
		}
	}
	return ""
}
func UnmarshalTargets(data []byte) (*Targets, error) {
	var targets Targets
	err := json.Unmarshal(data, &targets)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal Targets: %w", err)
	}
	return &targets, nil
}
