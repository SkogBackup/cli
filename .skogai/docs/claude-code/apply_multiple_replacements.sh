#!/bin/bash

# Script to apply multiple replacements to a single file
# Usage: ./apply_multiple_replacements.sh <target_file> <replacements_directory>

if [ $# -ne 2 ]; then
    echo "Usage: $0 <target_file> <replacements_directory>"
    echo "Example: $0 /path/to/file.txt /path/to/replacements/"
    echo ""
    echo "The replacements directory should contain pairs of files:"
    echo "  - Files starting with 'a' contain text to find"
    echo "  - Files starting with 'b' contain replacement text"
    echo "  - They are matched by the rest of their name after a/b"
    exit 1
fi

TARGET_FILE="$1"
REPLACEMENTS_DIR="$2"

# Check if target file exists
if [ ! -f "$TARGET_FILE" ]; then
    echo "Error: Target file '$TARGET_FILE' does not exist"
    exit 1
fi

# Check if replacements directory exists
if [ ! -d "$REPLACEMENTS_DIR" ]; then
    echo "Error: Replacements directory '$REPLACEMENTS_DIR' does not exist"
    exit 1
fi

# Create backup
cp "$TARGET_FILE" "$TARGET_FILE.backup"
echo "Created backup: $TARGET_FILE.backup"
echo

# Create temporary perl script to handle complex replacements
PERL_SCRIPT=.skogai/tmp/multi_replace_$$.pl"
cat > "$PERL_SCRIPT" << 'EOF'
#!/usr/bin/perl
use strict;
use warnings;
use File::Basename;

my $target_file = $ARGV[0];
my $replacements_dir = $ARGV[1];

# Read the target file content
open(my $fh, '<', $target_file) or die "Cannot open $target_file: $!";
my $content = do { local $/; <$fh> };
close($fh);

my $total_replacements = 0;
my $pairs_processed = 0;

# Find all 'a' files in the directory
opendir(my $dh, $replacements_dir) or die "Cannot open directory $replacements_dir: $!";
my @a_files = grep { /^a/ && -f "$replacements_dir/$_" } readdir($dh);
closedir($dh);

foreach my $a_file (@a_files) {
    # Extract the suffix after 'a'
    my $suffix = substr($a_file, 1);
    my $b_file = "b$suffix";
    
    my $a_path = "$replacements_dir/$a_file";
    my $b_path = "$replacements_dir/$b_file";
    
    # Check if corresponding b file exists
    if (-f $b_path) {
        # Read find text
        open(my $fh_a, '<', $a_path) or die "Cannot open $a_path: $!";
        my $find_text = do { local $/; <$fh_a> };
        close($fh_a);
        
        # Read replace text
        open(my $fh_b, '<', $b_path) or die "Cannot open $b_path: $!";
        my $replace_text = do { local $/; <$fh_b> };
        close($fh_b);
        
        # Remove trailing newlines if present
        $find_text =~ s/\n$//;
        $replace_text =~ s/\n$//;
        
        # Skip if find text is empty
        if (length($find_text) > 0) {
            # Escape special regex characters
            my $find_pattern = quotemeta($find_text);
            
            # Count replacements
            my $count = 0;
            $count++ while $content =~ s/$find_pattern/$replace_text/g;
            
            if ($count > 0) {
                print "✓ Replaced $count occurrence(s) from pair: $a_file -> $b_file\n";
                $total_replacements += $count;
            } else {
                print "- No matches found for pair: $a_file -> $b_file\n";
            }
            $pairs_processed++;
        } else {
            print "⚠ Skipping empty 'a' file: $a_file\n";
        }
    } else {
        print "⚠ No matching 'b' file for: $a_file (expected: $b_file)\n";
    }
}

# Write the modified content back
if ($total_replacements > 0) {
    open(my $out_fh, '>', $target_file) or die "Cannot write to $target_file: $!";
    print $out_fh $content;
    close($out_fh);
    print "\n";
    print "=== Summary ===\n";
    print "Total replacement pairs processed: $pairs_processed\n";
    print "Total replacements made: $total_replacements\n";
    print "File updated: $target_file\n";
} else {
    print "\n";
    print "=== Summary ===\n";
    print "No replacements were made.\n";
    print "Pairs checked: $pairs_processed\n";
}
EOF

chmod +x "$PERL_SCRIPT"

echo "=== Processing Replacements ==="
echo "Target file: $TARGET_FILE"
echo "Replacements directory: $REPLACEMENTS_DIR"
echo "=============================="
echo

# Run the perl script
"$PERL_SCRIPT" "$TARGET_FILE" "$REPLACEMENTS_DIR"

# Clean up
rm -f "$PERL_SCRIPT"

echo
echo "Done! Original file backed up as: $TARGET_FILE.backup"
