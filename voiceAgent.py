from fintechagent import AllCustomers, Products, Customer
from fintechagent.agent import Sarvam, Agent
from fintechagent.audio import PlayAudio
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def match_product_to_lead(customer: Customer, products: Products):
    """Identify the most suitable product for a lead based on their segment."""
    return next((prod for prod in products.products if customer.segment == prod.segment), products.default_product)

def lead_generation_demo():
    logger.info("Initializing Voice AI Agent for Lead Generation")
    audio_player = PlayAudio()
    sarvam = Sarvam.from_env()
    agent = Agent(sarvam)

    welcome_audio = sarvam.tts("Welcome to our Fintech Lead Generation Demo!")
    audio_player.play(welcome_audio.audio)

    logger.info("Retrieving leads and products")
    db_url = os.getenv("DB_URL")
    leads = AllCustomers.fetch_from_db(db_url)
    product_catalog = Products.fetch_from_folder("./products")

    for lead in leads.customers:
        recommended_product = match_product_to_lead(lead, product_catalog)
        logger.info("Engaging with lead: %s for product: %s", lead.name, recommended_product.title)
        agent.converse(lead, recommended_product)
        break  # For demonstration, stop after first lead

    logger.info("Lead Generation Demo Complete")

if __name__ == "__main__":
    lead_generation_demo()
