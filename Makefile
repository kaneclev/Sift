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

build: $(BUILD_DIR)
	cd $(PROJ_DIR) && go build -o ../../../$(BUILD_DIR)/$(APP_NAME)$(EXE_EXT)

run: build
	$(BUILD_DIR)/$(APP_NAME)$(EXE_EXT) --finput reddit --match-type loose

exec:
	$(BUILD_DIR)/$(APP_NAME)$(EXE_EXT) --finput ebay --match-type loose

clean:
	rm -rf $(BUILD_DIR)
