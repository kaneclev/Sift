package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

func argHandler(args []string) bool {
	success := true
	for idx := range args {
		arg := args[idx]
		if idx%2 == 0 {
			if (idx + 1) >= len(args) {
				fmt.Println("Expected an argument after: ", arg, idx+1, len(args))
				return false
			}
			is_set := mapArg(arg, args[idx+1])
			if !is_set {
				success = false
			}
		}
		continue
	}
	return success
	// we assume that the even values are keys and the odd values are values
}
func mapArg(option, value string) bool {
	clean_option := cleanOption(option)
	if clean_option == "" {
		return false
	}
	is_recognized := validateArgRecognition(clean_option)
	if !is_recognized {
		fmt.Println("Unrecognized option: ", clean_option)
		return false
	}

	err := os.Setenv(clean_option, value)
	if err != nil {
		fmt.Printf("\nCould not set argument %s = %s because: %v\n", clean_option, value, err)
		return false
	} else {
		fmt.Printf("\nRegistered argument %s = %s for this run\n", clean_option, value)
	}

	return true
}
func cleanOption(option string) string {
	split_option := strings.Split(option, "--")
	if len(split_option) != 2 {
		split_option = strings.Split(option, "-")
		if len(split_option) != 2 {
			fmt.Println("Please use '--' or '-' to denote options when passing arguments. Cannot parse options.")
			return ""
		}
	}
	return split_option[1]

}
func validateArgRecognition(arg string) bool {
	switch arg {
	case "finput":
		return true
	default:
		return false

	}
}

type EnvPair struct {
	KEY string
	VAL string
}

func defineEnvironment(relpath string) {
	to_define := getEnvironment(relpath)
	for _, pair := range to_define {
		if err := os.Setenv(pair.KEY, pair.VAL); err != nil {
			fmt.Printf("\nThere was an error setting the environment with the %s key, due to %v", pair.KEY, err)
		} else {
			fmt.Printf("\nDefined variable with key %s", pair.KEY)
		}
	}

}
func getEnvironment(relpath string) []EnvPair {
	file, err := os.Open(relpath)
	if err != nil {
		fmt.Printf("\nError opening file %s for environment variable loading: %v", relpath, err)
		return nil
	}
	defer file.Close()
	var envPairs []EnvPair
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			// then this isnt an env var
			continue
		}
		parts := getParts(line)
		key := strings.TrimSpace(parts[0])
		val := strings.TrimSpace(parts[1])
		// We are *assigning* the return of the append method back to envPairs cause append will deal with resizing the slice if needed, otherwise we would have to
		envPairs = append(envPairs, EnvPair{KEY: key, VAL: val})
	}
	if err := scanner.Err(); err != nil {
		fmt.Printf("\nCouldn't read environment, due to %v", err)
	}
	return envPairs
}
func getParts(to_split string) []string {
	return strings.SplitN(to_split, "=", 2)
}
