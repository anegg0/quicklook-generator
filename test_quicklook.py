import unittest
import os
from quicklook_generator import replace_with_quicklook

class TestQuicklookGenerator(unittest.TestCase):
    def setUp(self):
        # Sample test pairs (simulating glossary entries)
        self.test_pairs = [
            ('arbitrum', '<a data-quicklook-from="arbitrum">arbitrum</a>')
        ]
        
        # Read test input file
        with open('test_input.md', 'r') as f:
            self.test_content = f.read()
            
        # Generate output
        self.output = replace_with_quicklook(self.test_content, self.test_pairs)
        self.output_lines = self.output.split('\n')
        
    def test_single_occurrence(self):
        """Test that each term is only replaced once"""
        quicklook_count = self.output.count('data-quicklook-from="arbitrum"')
        self.assertEqual(quicklook_count, 1, "Term should only be replaced once")
        
    def test_link_adjacency(self):
        """Test that terms adjacent to links are not replaced"""
        for line in self.output_lines:
            if 'arbitrum next to link' in line:
                self.assertNotIn('data-quicklook-from', line, 
                               "Term adjacent to link should not be replaced")
                
    def test_code_block_protection(self):
        """Test that terms in code blocks are not replaced"""
        in_code_block = False
        for line in self.output_lines:
            if line.strip().startswith('```'):
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
                code_sections = line.split('`')
                for i in range(1, len(code_sections), 2):  # Check only code content
                    self.assertNotIn('data-quicklook-from', code_sections[i],
                                   "Terms in inline code should not be replaced")

if __name__ == '__main__':
    unittest.main() 