APP_NAME = siftrequests
BUILD_DIR = bin
MAIN = main
PROJ_DIR = ./src/scraping/go_requests

# Determine executable extension: .exe for Windows, nothing for others
ifeq ($(OS),Windows_NT)
	EXE_EXT = .exe
else
	EXE_EXT =
endif

# Ensure the bin directory exists
$(BUILD_DIR):
	mkdir $(BUILD_DIR)

build-go: $(BUILD_DIR)
	cd $(PROJ_DIR) && go build -o ../../../$(BUILD_DIR)/$(APP_NAME)$(EXE_EXT)
run-go: 
	$(BUILD_DIR)/$(APP_NAME)$(EXE_EXT) 


clean-builds:
	rm -rf $(BUILD_DIR)

start-sift: build-go
	.venv/Scripts/python make_sift.py ".venv/Scripts/python src/main.py" "./bin/siftrequests"