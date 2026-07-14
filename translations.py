"""
Lightweight UI translation dictionary (no external dependency, no build step).

Covers UI chrome (nav, footer, filters, pagination, etc.) only. Product
and category data come from Bol.com in Dutch and are intentionally left
untranslated, as are the legal pages.
"""

TRANSLATIONS = {
    'nl': {
        # Header
        'header.tagline': 'Vergelijk Witgoed',
        'search.placeholder': 'Zoek wasmachines, drogers...',
        'search.button': 'Zoeken',
        'nav.privacy': 'Privacy',
        'nav.disclaimer': 'Disclaimer',
        'nav.contact': 'Contact',
        'nav.guides': 'Gidsen',

        # Category nav (also reused in footer)
        'nav.wasmachines': 'Wasmachines',
        'nav.drogers': 'Drogers',
        'nav.wasdroogcombinaties': 'Combi Was-Droog',
        'nav.koelkasten': 'Koelkasten',
        'nav.vaatwassers': 'Vaatwassers',
        'nav.magnetrons': 'Magnetrons',
        'nav.ovens': 'Ovens & Airfryers',
        'nav.stofzuigers': 'Stofzuigers',
        'nav.koffiemachines': 'Koffiemachines',
        'nav.fornuizen': 'Fornuizen',
        'nav.kookplaten': 'Kookplaten',
        'nav.afzuigkappen': 'Afzuigkappen',

        # Footer
        'footer.about_title': 'Over WitgoedAanbod',
        'footer.about_text': 'WitgoedAanbod.nl helpt je de beste producten online vinden. Vergelijk prijzen, specificaties en reviews.',
        'footer.categories_title': 'Categorieën',
        'footer.legal_title': 'Juridisch',
        'footer.over_ons': 'Over ons',
        'footer.privacy': 'Privacybeleid',
        'footer.cookies': 'Cookiebeleid',
        'footer.cookie_settings': 'Cookievoorkeuren',
        'footer.disclaimer': 'Affiliate Disclaimer',
        'footer.terms': 'Algemene Voorwaarden',
        'footer.copyright': '© 2026 WitgoedAanbod.nl is deelnemer aan affiliate partnerprogramma. Als je via onze links iets koopt, ontvangen wij een kleine commissie, zonder extra kosten voor jou.',

        # Cookie modal
        'cookie.title': 'Cookie-instellingen',
        'cookie.intro': 'Op onze eigen pagina\'s plaatsen wij alleen noodzakelijke cookies. Klik je op een aanbieding, dan ga je naar Bol.com, MediaMarkt of Coolblue; die partijen kunnen je bezoek volgen om onze commissie te bepalen. Lees meer in ons',
        'cookie.policy_link': 'cookiebeleid',
        'cookie.essential_title': 'Noodzakelijke cookies',
        'cookie.essential_desc': 'Nodig om de site te laten werken: onthoudt je taalkeuze en deze cookiekeuze. Deze kun je niet uitzetten.',
        'cookie.analytics_title': 'Analytische cookies',
        'cookie.analytics_desc': 'Meten hoe bezoekers de site gebruiken. Wij gebruiken deze op dit moment niet; zetten we ze later aan, dan alleen met jouw toestemming.',
        'cookie.marketing_title': 'Marketingcookies',
        'cookie.marketing_desc': 'Voor gerichte advertenties. Wij plaatsen deze nu niet op onze eigen pagina\'s.',
        'cookie.reject': 'Alleen noodzakelijk',
        'cookie.save': 'Mijn keuze opslaan',
        'cookie.accept': 'Alles accepteren',

        # Filters
        'filters.title': 'Filters',
        'filters.min_price': 'Min. prijs',
        'filters.max_price': 'Max. prijs',
        'filters.brand': 'Merk',
        'filters.apply': 'Filter toepassen',

        # Sorting / results / pagination
        'sort.label': 'Sorteren op:',
        'sort.relevance': 'Relevantie',
        'sort.price_asc': 'Prijs: laag naar hoog',
        'sort.price_desc': 'Prijs: hoog naar laag',
        'results.count': 'resultaten',
        'pagination.prev': '← Vorige',
        'pagination.next': 'Volgende →',
        'pagination.page_of': 'Pagina {page} van {pages}',
        'products.none_found': 'Geen producten gevonden in deze categorie.',

        # Product cards / detail
        'product.brand_unknown': 'Merk onbekend',
        'product.in_stock': 'Op voorraad',
        'product.out_of_stock': 'Uitverkocht',
        'product.example_badge': 'Voorbeeldproduct',
        'product.example_badge_detail': 'Voorbeeldproduct — nog niet automatisch gesynchroniseerd',
        'product.description_title': 'Beschrijving',
        'product.specs_title': 'Specificaties',
        'product.related_title': 'Gerelateerde Producten',
        'product.compare_label': 'Vergelijken',
        'product.view_offer': 'Bekijk aanbieding',
        'product.show_more': 'Toon meer',
        'product.show_less': 'Toon minder',

        # Aanbiedingen / meerdere winkels
        'offer.best_price': 'Beste prijs',
        'offer.lowest_badge': 'Laagste prijs',
        'offer.from': 'vanaf',
        'offer.at_shops': 'bij {count} winkels',
        'offer.compare_cta': 'Vergelijk prijzen',
        'offer.view_at': 'Bekijk bij {retailer}',

        'compare.title': 'Vergelijk producten',
        'compare.empty': 'Geen producten geselecteerd om te vergelijken. Ga naar een categorie en vink "Vergelijk" aan bij maximaal 3 producten.',
        'compare.property': 'Eigenschap',

        # Search page
        'search.results_for': 'Zoekresultaten voor "{query}"',
        'search.results_found': 'resultaten gevonden',
        'search.category_label': 'Categorie',
        'search.all_categories': 'Alle categorieën',
        'search.no_results_title': 'Geen resultaten gevonden',
        'search.no_results_text': 'Probeer een ander zoekwoord of bekijk onze categorieën.',
        'search.back_home': 'Terug naar home',
        'product.affiliate_disclosure': 'WitgoedAanbod.nl is deelnemer aan de partnerprogramma\'s van de getoonde winkels. Als je via deze links iets koopt, ontvangen wij een kleine commissie, zonder extra kosten voor jou.',

        # Guides
        'guides.title': 'Koopgidsen',
        'guides.intro': 'Praktisch advies om de juiste keuze te maken, geschreven door WitgoedAanbod.nl.',
        'guides.read_more': 'Lees de gids →',
        'category.guide_teaser': 'Koopgids',
        'category.guide_teaser_cta': 'Lees onze gids',

        # Blog
        'blog.title': 'Blog & Nieuws',
        'blog.intro': 'Nieuwtjes over witgoed en uitgelichte producten, elke week bijgewerkt.',
        'blog.read_more': 'Lees meer →',
        'blog.chip': 'Nieuws',
        'home.blog_title': 'Laatste nieuws',

        # Homepage
        'home.usp1': 'Dagelijks actuele prijzen',
        'home.usp2': 'Onafhankelijk vergelijken',
        'home.usp3': 'Alle topmerken op één plek',
        'home.hero_title': 'Witgoed prijzen vergelijken',
        'home.hero_text': 'Vergelijk de prijzen van wasmachines, drogers, koelkasten en meer bij Bol, Coolblue en MediaMarkt — en vind de laagste prijs.',
        'home.hero_search_placeholder': 'Zoek een product...',
        'home.featured_title': 'Kijk en vergelijk: laagste prijzen, merken en levertijden',
        'home.categories_title': 'Populaire Categorieën',
        'home.categories_discover': 'Ontdek meer →',
        'home.about_title': 'Over WitgoedAanbod',
        'home.about_text': 'WitgoedAanbod.nl helpt je de beste witgoed producten vinden online. Vergelijk prijzen, specificaties en reviews.',
        'home.how_it_works_title': 'Hoe werkt WitgoedAanbod.nl?',
        'home.step1_title': '1. Zoeken',
        'home.step1_text': 'Zoek het product op de site.',
        'home.step2_title': '2. Vergelijken',
        'home.step2_text': 'Vergelijk specificaties, prijzen en reviews van verschillende merken.',
        'home.step3_title': '3. Koop het product',
        'home.step3_text': 'Klik door naar de aanbieder en koop direct.',
    },
    'en': {
        'header.tagline': 'Compare Appliances',
        'search.placeholder': 'Search washing machines, dryers...',
        'search.button': 'Search',
        'nav.privacy': 'Privacy',
        'nav.disclaimer': 'Disclaimer',
        'nav.contact': 'Contact',
        'nav.guides': 'Guides',

        'nav.wasmachines': 'Washing Machines',
        'nav.drogers': 'Dryers',
        'nav.wasdroogcombinaties': 'Washer-Dryers',
        'nav.koelkasten': 'Refrigerators',
        'nav.vaatwassers': 'Dishwashers',
        'nav.magnetrons': 'Microwaves',
        'nav.ovens': 'Ovens & Air Fryers',
        'nav.stofzuigers': 'Vacuum Cleaners',
        'nav.koffiemachines': 'Coffee Machines',
        'nav.fornuizen': 'Cookers',
        'nav.kookplaten': 'Hobs',
        'nav.afzuigkappen': 'Cooker Hoods',

        'footer.about_title': 'About WitgoedAanbod',
        'footer.about_text': 'WitgoedAanbod.nl helps you find the best products online. Compare prices, specifications and reviews.',
        'footer.categories_title': 'Categories',
        'footer.legal_title': 'Legal',
        'footer.over_ons': 'About us',
        'footer.privacy': 'Privacy Policy',
        'footer.cookies': 'Cookie Policy',
        'footer.cookie_settings': 'Cookie preferences',
        'footer.disclaimer': 'Affiliate Disclaimer',
        'footer.terms': 'Terms & Conditions',
        'footer.copyright': '© 2026 WitgoedAanbod.nl participates in an affiliate partner program. If you buy something through our links, we may earn a small commission, at no extra cost to you.',

        'cookie.title': 'Cookie settings',
        'cookie.intro': 'On our own pages we only place necessary cookies. When you click an offer you go to Bol.com, MediaMarkt or Coolblue; those parties may track your visit to determine our commission. Read more in our',
        'cookie.policy_link': 'cookie policy',
        'cookie.essential_title': 'Necessary cookies',
        'cookie.essential_desc': 'Needed for the site to work: they remember your language and this cookie choice. These cannot be switched off.',
        'cookie.analytics_title': 'Analytics cookies',
        'cookie.analytics_desc': 'Measure how visitors use the site. We do not use these at the moment; if we enable them later, it will only be with your consent.',
        'cookie.marketing_title': 'Marketing cookies',
        'cookie.marketing_desc': 'For targeted advertising. We do not place these on our own pages.',
        'cookie.reject': 'Necessary only',
        'cookie.save': 'Save my choice',
        'cookie.accept': 'Accept all',

        'filters.title': 'Filters',
        'filters.min_price': 'Min. price',
        'filters.max_price': 'Max. price',
        'filters.brand': 'Brand',
        'filters.apply': 'Apply Filters',

        'sort.label': 'Sort by:',
        'sort.relevance': 'Relevance',
        'sort.price_asc': 'Price: low to high',
        'sort.price_desc': 'Price: high to low',
        'results.count': 'results',
        'pagination.prev': '← Previous',
        'pagination.next': 'Next →',
        'pagination.page_of': 'Page {page} of {pages}',
        'products.none_found': 'No products found in this category.',

        'product.brand_unknown': 'Brand unknown',
        'product.in_stock': 'In stock',
        'product.out_of_stock': 'Out of stock',
        'product.example_badge': 'Example product',
        'product.example_badge_detail': 'Example product — not yet automatically synced',
        'product.description_title': 'Description',
        'product.specs_title': 'Specifications',
        'product.related_title': 'Related Products',
        'product.compare_label': 'Compare',
        'product.view_offer': 'View offer',
        'product.show_more': 'Show more',
        'product.show_less': 'Show less',

        # Offers / multiple shops
        'offer.best_price': 'Best price',
        'offer.lowest_badge': 'Lowest price',
        'offer.from': 'from',
        'offer.at_shops': 'at {count} shops',
        'offer.compare_cta': 'Compare prices',
        'offer.view_at': 'View at {retailer}',

        'compare.title': 'Compare products',
        'compare.empty': 'No products selected to compare. Go to a category and check "Compare" on up to 3 products.',
        'compare.property': 'Property',

        'search.results_for': 'Search results for "{query}"',
        'search.results_found': 'results found',
        'search.category_label': 'Category',
        'search.all_categories': 'All categories',
        'search.no_results_title': 'No results found',
        'search.no_results_text': 'Try a different search term or browse our categories.',
        'search.back_home': 'Back to home',
        'product.affiliate_disclosure': 'WitgoedAanbod.nl participates in the affiliate programs of the stores shown. If you buy something through these links, we may earn a small commission, at no extra cost to you.',

        'guides.title': 'Buying Guides',
        'guides.intro': 'Practical advice to help you choose, written by WitgoedAanbod.nl.',
        'guides.read_more': 'Read the guide →',
        'category.guide_teaser': 'Buying Guide',
        'category.guide_teaser_cta': 'Read our guide',

        'blog.title': 'Blog & News',
        'blog.intro': 'Appliance news and featured products, updated weekly.',
        'blog.read_more': 'Read more →',
        'blog.chip': 'News',
        'home.blog_title': 'Latest news',

        'home.usp1': 'Prices updated daily',
        'home.usp2': 'Independent comparison',
        'home.usp3': 'All top brands in one place',
        'home.hero_title': 'Compare Appliances & Household Devices',
        'home.hero_text': 'Find the best deals on washing machines, dryers, refrigerators and more. Look and compare.',
        'home.hero_search_placeholder': 'Search for a product...',
        'home.featured_title': 'Compare: lowest prices, brands and delivery times',
        'home.categories_title': 'Popular Categories',
        'home.categories_discover': 'Discover more →',
        'home.about_title': 'About WitgoedAanbod',
        'home.about_text': 'WitgoedAanbod.nl helps you find the best appliances online. Compare prices, specifications and reviews.',
        'home.how_it_works_title': 'How does WitgoedAanbod.nl work?',
        'home.step1_title': '1. Search',
        'home.step1_text': 'Search for the product on the site.',
        'home.step2_title': '2. Compare',
        'home.step2_text': 'Compare specifications, prices and reviews from different brands.',
        'home.step3_title': '3. Buy the product',
        'home.step3_text': 'Click through to the retailer and buy directly.',
    },
}


def translate(key, lang, **kwargs):
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS['nl'])
    text = lang_dict.get(key, TRANSLATIONS['nl'].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text
