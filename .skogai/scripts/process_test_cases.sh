#!/bin/bash

input_file="test_cases.txt"
output_file="tmp/test_results.txt"

total_lines=$(wc -l <"$input_file")
current_line=0

while IFS= read -r line || [ -n "$line" ]; do
  ((current_line++))
  echo "Processing line $current_line of $total_lines: $line"
  output=$(echo "$line" | skogparse --execute)
  echo "Output: $output"
  echo "$output" >>"$output_file"
done <"$input_file"
