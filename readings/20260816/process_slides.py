import re
import os

def process_file(input_path, output_path):
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
            # Each slide usually has English line, blank line, BM line
            lines = slide.split('\n')
            processed_lines = []
            
            # Identify which verse index we are in for Psalms
            is_psalms = section_id == 'psalms'
            verse_idx = i + 1
            is_second_verse = is_psalms and (verse_idx % 2 == 0)
            
            english_found = False
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    processed_lines.append(line)
                    continue
                
                # Check if it's a structural tag or separator (shouldn't be here but defensive)
                if stripped.startswith('<div') or stripped.startswith('</div'):
                    processed_lines.append(line)
                    continue

                if not english_found:
                    # English line
                    new_line = line
                    if is_second_verse:
                        # Wrap with {st}
                        # Preserve leading and trailing whitespace
                        match_leading = re.match(r'^(\s*)', line)
                        match_trailing = re.search(r'(\s*)$', line)
                        leading = match_leading.group(1) if match_leading else ""
                        trailing = match_trailing.group(1) if match_trailing else ""
                        content_only = line.strip()
                        new_line = f"{leading}{{st}}{content_only}{{/st}}{trailing}"
                    
                    processed_lines.append(new_line)
                    english_found = True
                else:
                    # BM line
                    match_leading = re.match(r'^(\s*)', line)
                    match_trailing = re.search(r'(\s*)$', line)
                    leading = match_leading.group(1) if match_leading else ""
                    trailing = match_trailing.group(1) if match_trailing else ""
                    content_only = line.strip()
                    
                    if is_second_verse:
                        # Order: {y}{it}{st}...{/st}{/y}{/it}
                        new_line = f"{leading}{{y}}{{it}}{{st}}{content_only}{{/st}}{{/y}}{{/it}}{trailing}"
                    else:
                        # Order: {y}{it}...{/y}{/it}
                        new_line = f"{leading}{{y}}{{it}}{content_only}{{/y}}{{/it}}{trailing}"
                    
                    processed_lines.append(new_line)
            
            processed_slides.append("\n".join(processed_lines))
        
        return header + "[===]".join(processed_slides) + footer

    # Apply processing to each section
    processed_content = div_pattern.sub(process_section, content)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(processed_content)

if __name__ == "__main__":
    # Use the directory where the script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, "input.html")
    output_file = os.path.join(base_dir, "output.html")
    process_file(input_file, output_file)
    print(f"Processed {input_file} into {output_file}")
