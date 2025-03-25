package get

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/projectdiscovery/katana/pkg/navigation"
)

// ParsedResponse organizes the data into logical “groups”.
type ParsedResponse struct {
	BasicInfo   BasicInfo            `json:"basic_info"`
	HeadersInfo HeadersInfo          `json:"headers"`
	BodyInfo    BodyInfo             `json:"body"`
	Forms       []navigation.Form    `json:"forms,omitempty"`
	XhrRequests []navigation.Request `json:"xhr_requests,omitempty"`
	Tech        []string             `json:"technologies,omitempty"`
	// If you want the raw content or path, you can track those as well:
	Raw                string `json:"raw,omitempty"`
	StoredResponsePath string `json:"stored_response_path,omitempty"`
}

// BasicInfo captures high-level response metadata
type BasicInfo struct {
	URL           string `json:"url"`
	Alias         string `json:"alias"`
	StatusCode    int    `json:"status_code"`
	ContentLength int64  `json:"content_length"`
}

// HeadersInfo captures each header key-value pair
type HeadersInfo struct {
	Entries navigation.Headers `json:"entries"`
}

// BodyInfo can hold the entire body or a snippet, depending on your needs
type BodyInfo struct {
	Text string `json:"text,omitempty"`
	// If you wanted to parse out links, Title, etc., you might add fields here.
}

func ParseResponse(resp *navigation.Response, alias string) (ParsedResponse, error) {
	// 1) Basic metadata grouping
	basic := BasicInfo{
		URL:           resp.Resp.Request.URL.String(),
		Alias:         alias,
		StatusCode:    resp.StatusCode,
		ContentLength: resp.ContentLength,
	}

	// 2) Headers grouping
	headers := HeadersInfo{
		Entries: resp.Headers,
	}

	// 3) Body grouping
	body := BodyInfo{
		Text: resp.Body, // or a truncated snippet if you prefer
	}

	// 4) Put everything into a single struct
	parsed := ParsedResponse{
		BasicInfo:          basic,
		HeadersInfo:        headers,
		BodyInfo:           body,
		Forms:              resp.Forms,
		XhrRequests:        resp.XhrRequests,
		Tech:               resp.Technologies,
		Raw:                resp.Raw,
		StoredResponsePath: resp.StoredResponsePath,
	}

	// If you want to do any further parsing or transformation—e.g. extracting links,
	// scanning for certain keywords, etc.—you can do that here before returning.

	return parsed, nil
}

// Here’s an example of how to actually write the structured result out to a file
func SaveParsedResponseToFile(parsed ParsedResponse, filename string) error {
	fileData, err := json.MarshalIndent(parsed, "", "  ")
	if err != nil {
		return err
	}

	if err := os.WriteFile(filename, fileData, 0644); err != nil {
		return err
	}
	fmt.Printf("\nSaved parsed response to %s\n", filename)
	return nil
}

// Example usage within your callback or anywhere else:
