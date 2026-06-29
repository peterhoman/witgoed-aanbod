"""
Claude API Integration for AI Content Generation
Generates product descriptions, meta tags, and guides
"""

import os
from anthropic import Anthropic

class AIContentGenerator:
    """Generate AI content using Claude API"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = Anthropic()

    def generate_product_description(self, product_title, product_type, brand=""):
        """Generate detailed product description"""
        prompt = f"""
Schrijf een professionele, SEO-geoptimaliseerde product beschrijving (200-300 woorden) voor:
- Product: {product_title}
- Type: {product_type}
- Merk: {brand or 'Onbekend'}

Beschrijving moet informatief, aantrekkelijk en sales-gericht zijn.
Sluit af met call-to-action: "Bekijk nu op Bol.com"
"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=400,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.content[0].text

    def generate_meta_description(self, product_title, product_type, price=None):
        """Generate SEO meta description (150-160 chars)"""
        prompt = f"""
Schrijf een SEO meta description (MAXIMAAL 160 karakters) voor:
- Product: {product_title}
- Type: {product_type}
{"- Prijs: €" + str(price) if price else ""}

Moet aantrekkelijk, duidelijk en keyword-rich zijn.
Alleen de description, geen extra tekst.
"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        text = response.content[0].text.strip()
        # Truncate to 160 chars
        return text[:160]

    def generate_buying_guide(self, category):
        """Generate buying guide for a category"""
        prompt = f"""
Schrijf een praktische buying guide voor {category} (300-400 woorden).
Include:
- Wat zijn de belangrijkste kenmerken?
- Hoe kies je de juiste voor jou?
- Waar op letten?
- Tips & tricks

Schrijf in Nederlands, informeel maar professioneel.
"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=600,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.content[0].text

    def generate_comparison(self, product_a, product_b, category):
        """Generate product comparison"""
        prompt = f"""
Vergelijk deze twee {category} producten (200-250 woorden):
- Product A: {product_a}
- Product B: {product_b}

Format:
- Overeenkomsten
- Verschillen
- Welke is beter voor wie?
- Conclusie

Schrijf in Nederlands.
"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=400,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.content[0].text


def generate_for_product(product):
    """Generate all content for a product"""
    try:
        generator = AIContentGenerator()

        # Generate description
        description = generator.generate_product_description(
            product.title,
            product.subcategory or product.category.name,
            product.brand
        )

        # Generate meta description
        meta_description = generator.generate_meta_description(
            product.title,
            product.category.name,
            product.price
        )

        return {
            'description': description,
            'meta_description': meta_description
        }

    except Exception as e:
        print(f"[!] Error generating content for {product.title}: {e}")
        return None


if __name__ == '__main__':
    # Test
    generator = AIContentGenerator()
    desc = generator.generate_product_description("Samsung WW90T534DAW", "Wasmachine", "Samsung")
    print(desc)
