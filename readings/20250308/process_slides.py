import re
import os

def process_file(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by div sections
    div_pattern = re.compile(r'(<div id="(ot|nt|gospel|Psalms)">)(.*?)(</div>)', re.DOTALL | re.IGNORECASE)
    
    def process_section(match):
        header = match.group(1)
        section_id = match.group(2).lower()
        body = match.group(3)
        footer = match.group(4)
        
        # Split by slide separator [===]
        slides = body.split('[===]')
        processed_slides = []
        
        for i, slide in enumerate(slides):
            # Each slide usually has English line(s), blank line(s), BM line(s)
            # We split by double newlines or single newlines to identify "verse blocks"
            # However, looking at the input, verses are separated by empty lines (often just \n\n)
            
            # Divide into blocks of content separated by blank lines
            raw_blocks = re.split(r'\n\s*\n', slide.strip())
            # Clean up blocks: remove leading/trailing whitespace from each block
            blocks = [b.strip() for b in raw_blocks if b.strip()]
            
            processed_blocks = []
            
            # Identify which verse index we are in for Psalms
            is_psalms = section_id == 'psalms'
            verse_idx = i + 1
            is_second_verse = is_psalms and (verse_idx % 2 == 0)
            
            if len(blocks) >= 1:
                # First block is English
                english_content = blocks[0]
                if is_second_verse:
                    processed_blocks.append(f"{{st}}{english_content}{{/st}}")
                else:
                    processed_blocks.append(english_content)
                
            if len(blocks) >= 2:
                # Second block is BM
                bm_content = blocks[1]
                if is_second_verse:
                    processed_blocks.append(f"{{y}}{{it}}{{st}}{bm_content}{{/st}}{{/y}}{{/it}}")
                else:
                    processed_blocks.append(f"{{y}}{{it}}{bm_content}{{/y}}{{/it}}")
            
            # Reconstruct the slide with a single blank line between blocks
            slide_content = "\n\n".join(processed_blocks)
            
            # Add back some padding to match original style if needed
            # (The original usually has leading/trailing newlines)
            processed_slides.append("\n\n" + slide_content + "\n")
        
        return header + "[===]".join(processed_slides) + footer

    # Apply processing to each section
    processed_content = div_pattern.sub(process_section, content)
    
    # Simple cleanup to remove excess whitespace between tags if any was introduced
    # but maintaining structural spacing
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(processed_content)

if __name__ == "__main__":
    # Use current directory files if they exist, otherwise fallback or exit
    cwd = os.getcwd()
    input_file = os.path.join(cwd, "input.html")
    output_file = os.path.join(cwd, "output.html")
    
    if os.path.exists(input_file):
        process_file(input_file, output_file)
        print(f"Processed {input_file} into {output_file}")
    else:
        print(f"Error: input.html not found in {cwd}")
