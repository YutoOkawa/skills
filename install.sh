#!/bin/bash

# Exit on error
set -e

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SRC_DIR="${SCRIPT_DIR}/skills"
INSTALL_DEST="${HOME}/.gemini/config/skills"

# Function to show help
show_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -s, --symlink      Install skills as symbolic links (default, recommended for development)"
    echo "  -c, --copy         Install skills by copying files"
    echo "  -u, --uninstall    Uninstall skills from the agy config directory"
    echo "  -k, --skill NAME   Target a specific skill (default: all skills)"
    echo "  -f, --force        Force overwrite existing files/links without prompting"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Install all skills as symlinks"
    echo "  $0 --copy          # Install all skills by copying"
    echo "  $0 -k discord-messenger --symlink"
    echo "  $0 --uninstall -k discord-messenger"
}

# Default values
MODE="symlink"
ACTION="install"
TARGET_SKILL=""
FORCE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -s|--symlink)
            MODE="symlink"
            shift
            ;;
        -c|--copy)
            MODE="copy"
            shift
            ;;
        -u|--uninstall)
            ACTION="uninstall"
            shift
            ;;
        -k|--skill)
            TARGET_SKILL="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Error: Unknown option $1"
            show_help
            exit 1
            ;;
    esac
done

# Create destination directory if installing
if [ "${ACTION}" = "install" ]; then
    mkdir -p "${INSTALL_DEST}"
fi

# Get list of skills
if [ -n "${TARGET_SKILL}" ]; then
    if [ ! -d "${SKILLS_SRC_DIR}/${TARGET_SKILL}" ]; then
        echo "Error: Skill '${TARGET_SKILL}' does not exist in ${SKILLS_SRC_DIR}"
        exit 1
    fi
    SKILLS=("${TARGET_SKILL}")
else
    # Find all subdirectories in skills/
    SKILLS=()
    if [ -d "${SKILLS_SRC_DIR}" ]; then
        for dir in "${SKILLS_SRC_DIR}"/*; do
            if [ -d "${dir}" ]; then
                SKILLS+=("$(basename "${dir}")")
            fi
        done
    else
        echo "Error: ${SKILLS_SRC_DIR} directory not found."
        exit 1
    fi
fi

if [ ${#SKILLS[@]} -eq 0 ]; then
    echo "No skills found to process."
    exit 0
fi

# Process each skill
for skill in "${SKILLS[@]}"; do
    SRC_PATH="${SKILLS_SRC_DIR}/${skill}"
    DEST_PATH="${INSTALL_DEST}/${skill}"

    if [ "${ACTION}" = "install" ]; then
        echo "Installing skill: ${skill} using ${MODE}..."
        
        # Check if already exists
        if [ -e "${DEST_PATH}" ] || [ -L "${DEST_PATH}" ]; then
            if [ "$FORCE" = true ]; then
                rm -rf "${DEST_PATH}"
            else
                read -p "Warning: ${DEST_PATH} already exists. Overwrite? [y/N]: " choice
                case "$choice" in
                    [yY][eE][sS]|[yY])
                        rm -rf "${DEST_PATH}"
                        ;;
                    *)
                        echo "Skipping ${skill}."
                        continue
                        ;;
                esac
            fi
        fi

        # Install based on mode
        if [ "${MODE}" = "symlink" ]; then
            ln -s "${SRC_PATH}" "${DEST_PATH}"
            echo "Successfully symlinked: ${DEST_PATH} -> ${SRC_PATH}"
        else
            cp -R "${SRC_PATH}" "${DEST_PATH}"
            echo "Successfully copied: ${SRC_PATH} -> ${DEST_PATH}"
        fi

    elif [ "${ACTION}" = "uninstall" ]; then
        echo "Uninstalling skill: ${skill}..."
        if [ -e "${DEST_PATH}" ] || [ -L "${DEST_PATH}" ]; then
            rm -rf "${DEST_PATH}"
            echo "Successfully removed: ${DEST_PATH}"
        else
            echo "Skill '${skill}' is not installed (no entry at ${DEST_PATH})"
        fi
    fi
done

echo "Operation completed successfully!"
