import os
import re
from playwright.sync_api import sync_playwright

def apply_formatting(text, is_bold=False):
    """Standardizes OpenLP tags and handles bilingual formatting logic."""
    text = re.sub(r'\{/?(y|it|st|su|b|i)\}', '', text)
    blocks = [b.strip() for b in text.split('\n') if b.strip()]
    
    processed_blocks = []
    for i, block in enumerate(blocks):
        block = re.sub(r'(\d+:\d+)', r'<sup>\1</sup>', block)
        if i % 2 == 1: # BM text
            content = f'<span class="yellow"><i>{block}</i></span>'
        else: # English text
            content = block
        
        if is_bold:
            content = f'<b>{content}</b>'
            
        processed_blocks.append(content)
    
    return '<br><br>'.join(processed_blocks)

def generate_slides(html_file, output_folder):
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all div sections with specific IDs
    sections = re.findall(r'<div id="(ot|nt|gospel|psalms)"[^>]*>(.*?)</div>', content, re.DOTALL | re.IGNORECASE)

    if not sections:
        # Fallback to splitting by [===] if no sections found
        sections = [('slide', content)]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        for section_name, section_content in sections:
            section_name = section_name.lower()
            section_dir = os.path.join(output_folder, section_name)
            if not os.path.exists(section_dir):
                os.makedirs(section_dir)

            slides = [s.strip() for s in section_content.split('[===]') if s.strip()]
            
            for i, slide_raw in enumerate(slides):
                clean_slide = re.sub(r'<[^>]+>', '', slide_raw)
                # Psalms responsive reading: Congregation (even verse index, odd slide index i) gets bolded
                is_psalm_response = (section_name == 'psalms' and (i + 1) % 2 == 0)
                formatted_content = apply_formatting(clean_slide.strip(), is_bold=is_psalm_response)
                
                full_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{
                            background-color: black !important;
                            color: white;
                            font-family: 'Tahoma', 'Arial', sans-serif;
                            margin: 0;
                            padding: 80px 100px; /* Top/Bottom and Left/Right padding */
                            display: flex;
                            justify-content: flex-start;
                            align-items: flex-start;
                            height: 100vh;
                            width: 100vw;
                            overflow: hidden;
                            box-sizing: border-box;
                        }}
                        .slide-container {{
                            width: 100%;
                            font-size: 70px;
                            line-height: 1.3;
                            font-weight: 400; /* Normal weight for Minister */
                            text-align: left;
                        }}
                        .yellow {{ color: #FFFF00 !important; }}
                        i {{ font-style: italic; }}
                        b {{ font-weight: 900 !important; }} /* Extra heavy for Congregation */
                        sup {{ font-size: 0.5em; vertical-align: super; color: #888; margin-right: 10px; }}
                    </style>
                </head>
                <body>
                    <div class="slide-container">{formatted_content}</div>
                </body>
                </html>
                """
                
                page.set_content(full_html)
                page.wait_for_timeout(50)
                
                filename = f"{section_name}_{i+1:03d}.png"
                filepath = os.path.join(section_dir, filename)
                page.screenshot(path=filepath)
                print(f"Generated: {section_name}/{filename}")

        browser.close()

if __name__ == "__main__":
    cwd = os.getcwd()
    target_file = "input.html" if os.path.exists("input.html") else "output.html"
    output_dir = os.path.join(cwd, "images")
    
    print(f"Generating sectioned slides from {target_file}...")
    generate_slides(os.path.join(cwd, target_file), output_dir)
    print(f"Success! Images saved in: {output_dir}")
