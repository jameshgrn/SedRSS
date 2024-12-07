import pandas as pd
import json
from parser import _remove_html_tags, _standardize_abstract, _standardize_date, _standardize_authors, parse_journal_rss
from summarizer import generate_greeting
from pprint import pprint
from formatter import format_for_quarto


keywords = [
    "sedimentology",
    "alluvial_fan",
    "debris_flow",
    "fluvial"
    "fluvial_geomorphology",
    "stratigraphy",
    "delta",
    "river",
    "mouth_bar",
    "bifurcation",
    "braided_river",
    "braid_bar",
    "bar_theory",
    "bar_formation",
    "bar_morphology",
    "bar_migration",
    "bar,"
    "sediment",
    "sedimentary",
    "sediment_transport",
    "sand_mining",
    "tectonic_geomorphology",
    "earth_surface_processes",
    "river_channels",
    "river_morphodynamics",
    "delta_formation",
    "avulsion",
    "morphodynamics",
    "alluvial_dynamics",
    "sedimentary_rocks",
    "erosion",
    "deposition",
    "sediment_analysis",
    "fluvial_deposits",
    "sedimentation",
    "sequence_stratigraphy",
    "stratigraphic_analysis",
    "sediment_composition",
    "sediment_transport_modeling",
    "geomorphic_evolution",
    "sedimentary_basins",
    "river_morphology",
    "sediment_deposition",
    "fluvial_erosion",
    "sediment_sorting",
    "sedimentary_petrology",
    "bedrock_erosion",
    "sediment_dynamics",
    "sedimentary_facies",
    "sedimentary_structures",
    "sedimentary_environments",
    "sediment_flux",
    "sedimentology_research",
    "sedimentology_techniques",
    "sedimentary_records",
    "sediment_transport_mechanisms",
    "sedimentary_archives",
    "geomorphological",
    "source-to-sink",
    "sedimentary_analysis_methods",
    "paleo-geomorphology",
    "coastal_geomorphology",
    "sediment_core_analysis",
    "lacustrine_sedimentology",
    "eolian",
    "geochemical_sediment_analysis",
    "paleoflood_analysis",
    "quaternary_sedimentology",
    "hydrogeology",
    "submarine_geomorphology",
    "sediment_budget_analysis",
]



df = pd.read_csv('journals.csv')
df['Format'] = df['Format'].astype(int)  # Convert the Format column to integers
format_set = set()  # To keep track of encountered formats
all_new_articles = []

for i, row in df.iterrows():
    journal_title = row['Journal Name']
    url = row['RSS URL']
    format_int = row['Format']
    
    # Check if the format has already been encountered
    if format_int not in format_set:
        journal_articles = parse_journal_rss(journal_title, url, format_int=format_int)
        all_new_articles += journal_articles
        format_set.add(format_int)  # Add the format to the set

for article in all_new_articles:
    article['Published Date'] = _standardize_date(article['Published Date'])
    article['Authors'] = _standardize_authors(article['Authors'])
    article['Abstract'] = _remove_html_tags(_standardize_abstract(article['Abstract']))

greeting, top_articles, median_articles = generate_greeting(all_new_articles, keywords=keywords)
quarto_file = format_for_quarto(greeting, median_articles)

#save quarto file
with open('quarto_file4.qmd', 'w') as f:
    f.write(quarto_file)
