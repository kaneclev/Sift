APP_NAME = siftrequests
BUILD_DIR = bin
MAIN = main
PROJ_DIR = ./src/scraping/go_requests

# Determine executable extension: .exe for Windows, nothing for others
ifeq ($(OS),Windows_NT)
	EXE_EXT = .exe
	VENV_PY = Scripts
else
	EXE_EXT =
	VENV_PY = bin
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
	.venv/$(VENV_PY)/python make_sift.py ".venv/$(VENV_PY)/python src/main.py" "./bin/siftrequests"


