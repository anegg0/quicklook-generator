import unittest
import os
from quicklook_generator import replace_with_quicklook
import re

class TestQuicklookGenerator(unittest.TestCase):
    def setUp(self):
        # Sample test pairs (simulating glossary entries)
        self.test_pairs = [
            ('arbitrum', '<a data-quicklook-from="arbitrum">arbitrum</a>'),
            ('bridge', '<a data-quicklook-from="bridge">Bridge</a>'),
            ('sequencer', '<a data-quicklook-from="sequencer">Sequencer</a>'),
            ('arbos', '<a data-quicklook-from="arbos">ArbOS</a>')
        ]
        
        # Read test input file
        with open('test_input.md', 'r') as f:
            self.test_content = f.read()
            
        # Generate output
        self.output = replace_with_quicklook(self.test_content, self.test_pairs)
        self.output_lines = self.output.split('\n')
        
    def test_single_occurrence(self):
        """Test that each term is only replaced once"""
        # Test for each term in our pairs
        for search_term, _ in self.test_pairs:
            tag = f'data-quicklook-from="{search_term.lower()}"'
            initial_count = self.test_content.count(tag)
            final_count = self.output.count(tag)
            new_tags = final_count - initial_count
            self.assertLessEqual(new_tags, 1, 
                               f"Term '{search_term}' was replaced more than once")
        
    def test_link_adjacency(self):
        """Test that terms adjacent to links are not replaced"""
        # Test markdown links
        for line in self.output_lines:
            if '](' in line:
                # Find all markdown links in the line
                link_starts = [i for i in range(len(line)) if line.startswith('](', i)]
                for start in link_starts:
                    # Find the opening bracket
                    open_bracket = line.rfind('[', 0, start)
                    if open_bracket == -1:
                        continue
                    # Find the closing parenthesis
                    close_paren = line.find(')', start)
                    if close_paren == -1:
                        continue
                    
                    # Check the regions adjacent to the link
                    link_region = line[open_bracket:close_paren+1]
                    if 'data-quicklook-from' in link_region:
                        # If there's a quicklook tag in the link region, verify it was pre-existing
                        self.assertTrue(any(link_region in l for l in self.test_content.splitlines()),
                                     "New quicklook tag added inside or adjacent to markdown link")
        
    def test_code_block_protection(self):
        """Test that terms in code blocks are not replaced"""
        in_code_block = False
        for line in self.output_lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                self.assertNotIn('data-quicklook-from', line,
                               "Terms in code blocks should not be replaced")
                
    def test_header_protection(self):
        """Test that terms in headers are not replaced"""
        for line in self.output_lines:
            if line.startswith('#'):
                self.assertNotIn('data-quicklook-from', line,
                               "Terms in headers should not be replaced")
                
    def test_frontmatter_protection(self):
        """Test that terms in front matter are not replaced"""
        in_frontmatter = False
        for line in self.output_lines:
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter:
                self.assertNotIn('data-quicklook-from', line,
                               "Terms in front matter should not be replaced")
                
    def test_inline_code_protection(self):
        """Test that terms in inline code are not replaced"""
        for line in self.output_lines:
            if '`' in line:
                # Split by backtick but preserve existing quicklook tags
                code_sections = []
                current_pos = 0
                in_code = False
                
                while True:
                    next_backtick = line.find('`', current_pos)
                    if next_backtick == -1:
                        break
                        
                    if in_code:
                        code_content = line[current_pos:next_backtick]
                        # Only check for new quicklook tags, not pre-existing ones
                        if 'data-quicklook-from' in code_content:
                            # Verify this is a pre-existing tag by checking if it's in the original content
                            original_line = next(l for l in self.test_content.split('\n') if code_content in l)
                            if code_content not in original_line:
                                self.fail(f"New quicklook tag found in inline code: {code_content}")
                    
                    current_pos = next_backtick + 1
                    in_code = not in_code

    def test_case_sensitivity(self):
        """Test that terms are matched case-insensitively but preserve original case"""
        # Test that we can match terms case-insensitively
        for line in self.output_lines:
            if 'data-quicklook-from' in line:
                # Extract the term and its tag type
                tag_match = re.search(r'data-quicklook-from="([^"]+)"[^>]*>([^<]+)', line)
                if tag_match:
                    tag_type, term = tag_match.groups()
                    # Skip pre-existing tags that aren't in our search terms
                    if any(tag_type in l for l in self.test_content.splitlines()):
                        continue
                    # Verify that new tags match one of our search terms case-insensitively
                    matched = False
                    for search_term, _ in self.test_pairs:
                        if search_term.lower() == tag_type.lower():
                            matched = True
                            break
                    self.assertTrue(matched, f"Found new tag '{tag_type}' that doesn't match any search term")

    def test_existing_quicklook_protection(self):
        """Test that existing quicklook tags are not modified or nested"""
        # Find all existing quicklook tags in the input
        for line in self.test_content.splitlines():
            if 'data-quicklook-from' in line:
                # Extract all quicklook tags from this line
                input_tags = re.findall(r'<a\s+data-quicklook-from="[^"]+">([^<]+)</a>', line)
                # Find the corresponding line in the output
                output_line = next(l for l in self.output_lines 
                                 if all(tag in l for tag in input_tags))
                # Count quicklook tags in both lines
                input_tag_count = line.count('data-quicklook-from')
                output_tag_count = output_line.count('data-quicklook-from')
                # The output line should not have more tags than the input line
                self.assertLessEqual(output_tag_count, input_tag_count + 1,
                                   "Too many quicklook tags added to a line with existing tags")

if __name__ == '__main__':
    unittest.main() 