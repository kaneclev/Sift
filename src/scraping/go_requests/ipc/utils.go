package ipc

import (
	"path/filepath"
)

func GetReturnJSONFilename(filename string) string {
	// TODO the sender and the reciever need an identifier ID at some point (perhaps not necessarily strictly thru files but maybe thru socket or otherwise) t
	// to identify what file the content was returned to them as
	return filepath.Join("RequestPipe", "Returned", filename+".json")
}
