#!/bin/bash
# Line counting script for files and directories

# Function to count lines in a file
count_lines_in_file() {
    local file="$1"

    if [ ! -f "$file" ]; then
        echo "Error: File $file does not exist"
        return 1
    fi

    # Count total lines
    local total_lines=$(wc -l < "$file")

    # Count blank lines
    local blank_lines=$(grep -c "^[[:space:]]*$" "$file")

    # Count comment lines (basic detection)
    local comment_lines=0
    local ext="${file##*.}"

    case "$ext" in
        py|sh|bash|rb)
            comment_lines=$(grep -c "^[[:space:]]*#" "$file")
            ;;
        js|java|c|cpp|h|php)
            comment_lines=$(grep -c "^[[:space:]]*//" "$file")
            comment_lines=$((comment_lines + $(grep -c "^[[:space:]]*/\\*" "$file")))
            ;;
        html|xml)
            comment_lines=$(grep -c "^[[:space:]]*<!--" "$file")
            ;;
    esac

    # Calculate code lines
    local code_lines=$((total_lines - blank_lines - comment_lines))

    echo "File: $file"
    echo "  Total lines: $total_lines"
    echo "  Code lines: $code_lines"
    echo "  Blank lines: $blank_lines"
    echo "  Comment lines: $comment_lines"
}

# Function to count lines in all files in a directory
count_lines_in_directory() {
    local dir="$1"
    local extensions="$2"

    if [ ! -d "$dir" ]; then
        echo "Error: Directory $dir does not exist"
        return 1
    fi

    echo "Scanning directory: $dir"

    local total_files=0
    local total_lines=0
    local total_blank=0
    local total_comments=0
    local total_code=0

    # Create a temporary file to store results
    local temp_file=$(mktemp)

    # Find files and process them
    if [ -z "$extensions" ]; then
        # Process all text files
        find "$dir" -type f -size -1M | while read -r file; do
            # Skip binary files (simple check)
            if file "$file" | grep -q "text"; then
                process_file "$file" >> "$temp_file"
            fi
        done
    else
        # Process only files with specified extensions
        local ext_pattern=$(echo "$extensions" | sed 's/,/\\|/g')
        find "$dir" -type f -size -1M -name "*.$ext_pattern" | while read -r file; do
            process_file "$file" >> "$temp_file"
        done
    fi

    # Display results
    if [ -s "$temp_file" ]; then
        cat "$temp_file"

        # Calculate totals
        total_files=$(grep -c "^File:" "$temp_file")
        total_lines=$(grep "Total lines:" "$temp_file" | awk '{sum += $3} END {print sum}')
        total_blank=$(grep "Blank lines:" "$temp_file" | awk '{sum += $3} END {print sum}')
        total_comments=$(grep "Comment lines:" "$temp_file" | awk '{sum += $3} END {print sum}')
        total_code=$(grep "Code lines:" "$temp_file" | awk '{sum += $3} END {print sum}')

        # Print summary
        echo -e "\nSummary:"
        echo "  Total files: $total_files"
        echo "  Total lines: $total_lines"
        echo "  Code lines: $total_code"
        echo "  Blank lines: $total_blank"
        echo "  Comment lines: $total_comments"

        if [ "$total_lines" -gt 0 ]; then
            echo -e "\nPercentages:"
            echo "  Code: $(awk -v code=$total_code -v total=$total_lines 'BEGIN {printf "%.1f", (code/total*100)}')%"
            echo "  Comments: $(awk -v comments=$total_comments -v total=$total_lines 'BEGIN {printf "%.1f", (comments/total*100)}')%"
            echo "  Blank: $(awk -v blank=$total_blank -v total=$total_lines 'BEGIN {printf "%.1f", (blank/total*100)}')%"
        fi
    else
        echo "No files found or processed."
    fi

    # Clean up
    rm -f "$temp_file"
}

# Function to process a single file
process_file() {
    local file="$1"

    # Count total lines
    local total_lines=$(wc -l < "$file" 2>/dev/null || echo 0)

    # Count blank lines
    local blank_lines=$(grep -c "^[[:space:]]*$" "$file" 2>/dev/null || echo 0)

    # Count comment lines (basic detection)
    local comment_lines=0
    local ext="${file##*.}"

    case "$ext" in
        py|sh|bash|rb)
            comment_lines=$(grep -c "^[[:space:]]*#" "$file" 2>/dev/null || echo 0)
            ;;
        js|java|c|cpp|h|php)
            comment_lines=$(grep -c "^[[:space:]]*//" "$file" 2>/dev/null || echo 0)
            comment_lines=$((comment_lines + $(grep -c "^[[:space:]]*/\\*" "$file" 2>/dev/null || echo 0)))
            ;;
        html|xml)
            comment_lines=$(grep -c "^[[:space:]]*<!--" "$file" 2>/dev/null || echo 0)
            ;;
    esac

    # Calculate code lines
    local code_lines=$((total_lines - blank_lines - comment_lines))

    # Print results for this file
    echo "File: $file"
    echo "  Total lines: $total_lines"
    echo "  Code lines: $code_lines"
    echo "  Blank lines: $blank_lines"
    echo "  Comment lines: $comment_lines"
    echo ""
}

# Main function
main() {
    if [ $# -eq 0 ]; then
        echo "Usage: count_lines [file_or_directory] [extensions]"
        echo "Examples:"
        echo "  count_lines myfile.py"
        echo "  count_lines src/"
        echo "  count_lines src/ py,js,html"
        return 1
    fi

    local path="$1"
    local extensions="$2"

    if [ -f "$path" ]; then
        # Count lines in a single file
        count_lines_in_file "$path"
    elif [ -d "$path" ]; then
        # Count lines in a directory
        count_lines_in_directory "$path" "$extensions"
    else
        echo "Error: $path does not exist"
        return 1
    fi
}

# Run the script
main "$@"
