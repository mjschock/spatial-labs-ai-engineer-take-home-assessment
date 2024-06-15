import json
import os
from typing import List, Literal, Optional

from llama_index.core.indices import MultiModalVectorStoreIndex
from llama_index.core.schema import NodeRelationship, ObjectType
from llama_index.core.vector_stores.types import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
    FilterCondition,
)
from llama_index.vector_stores.postgres import PGVectorStore
import marvin
from pydantic import BaseModel
from sqlalchemy import make_url

POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

class Product(BaseModel):
    _id: str
    name: str
    # image_url: str
    price: str|float # TODO: use price_USD_high and price_USD_low instead?
    caption: Optional[str] = None
    classification: str
    color: str
    item_type: str
    materials: str
    rating: str|float
    style: str

def get_index():
    connection_string = f"postgresql://postgres:{POSTGRES_PASSWORD}@localhost:5432"
    db_name = "vector_db"
    url = make_url(connection_string)

    text_store = PGVectorStore.from_params(
        database=db_name,
        host=url.host,
        password=url.password,
        port=url.port,
        user=url.username,
        table_name="llama_index_text_node_collection",
        embed_dim=1536,  # openai embedding dimension
        # hybrid_search
        # use_jsonb
    )

    image_store = PGVectorStore.from_params(
        database=db_name,
        host=url.host,
        password=url.password,
        port=url.port,
        user=url.username,
        table_name="llama_index_image_node_collection",
        embed_dim=512,  # openai embedding dimension
    )

    return MultiModalVectorStoreIndex.from_vector_store(
        vector_store=text_store, image_vector_store=image_store,
    )

# The user should be able to inquire about products in the catalog, request 
# detailed information about specific products, receive recommendations for 
# similar products, or search for products based on preferences such as color 
# (e.g., "red") or item type (e.g., "shoe").
def get_products(
    _ids: Optional[List[str]] = None,
    classification: Optional[str] = None,
    color: Optional[str] = None,
    image_url: Optional[str] = None,
    image_similarity_top_k: Optional[int] = 0,
    item_type: Optional[str] = None,
    materials: Optional[str] = None,
    max_price: Optional[str|float] = None,
    max_rating: Optional[str|float] = None,
    min_price: Optional[str|float] = None,
    min_rating: Optional[str|float] = None,
    name: Optional[str] = None, 
    style: Optional[str] = None,
    text_similarity_top_k: Optional[int] = None,
) -> List[Product]:
    """Get products that optionally match the specified criteria. If no criteria are specified, all products are returned.

    Parameters
    ----------
    _ids : List[str]
        The IDs of the products to return
    classification : str
        The classification of the product
    color : str
        The color of the product
    image_url : str
        The image URL of a similar product
    image_similarity_top_k : int
        The number of visually similar products to return
    item_type : str
        The type of the product
    materials : str
        The materials of the product
    max_price : str
        The maximum price of the product
    max_rating : str
        The maximum rating of the product
    min_price : str
        The minimum price of the product
    min_rating : str
        The minimum rating of the product
    name : str
        The name of the product
    style : str
        The style of the product
    text_similarity_top_k : int
        The number of textually similar products to return

    Returns
    -------
    List[Product]
        The products that match the specified criteria
    """
    filters = []
    metadata = {}

    if classification is not None:
    #     # filters.append(MetadataFilter(
    #     #     key="classification",
    #     #     operator=FilterOperator.TEXT_MATCH, # Unknown operator: FilterOperator.TEXT_MATCH, fallback to '='
    #     #     value=classification,
    #     # ))
        metadata["classification"] = classification

    if color is not None:
        # filters.append(MetadataFilter(
        #     key="color",
        #     operator=FilterOperator.IN,
        #     value=[color],
        # ))
        metadata["color"] = color

    if item_type is not None:
        metadata["item_type"] = item_type

    if materials is not None:
        metadata["materials"] = materials

    if max_price is not None:
        filters.append(MetadataFilter(
            # key="price",
            key="price_USD_high", # assuming price is in USD
            operator=FilterOperator.LTE,
            value=max_price,
        ))

    if max_rating is not None:
        filters.append(MetadataFilter(
            key="rating",
            operator=FilterOperator.LTE,
            value=max_rating,
        ))

    if min_price is not None:
        filters.append(MetadataFilter(
            # key="price",
            key="price_USD_low", # assuming price is in USD
            operator=FilterOperator.GTE,
            value=min_price,
        ))

    if min_rating is not None:
        filters.append(MetadataFilter(
            key="rating",
            operator=FilterOperator.GTE,
            value=min_rating,
        ))

    metadata_filters = MetadataFilters(
        filters=filters,
        condition=FilterCondition.AND,
    )

    # retriever = index.as_retriever(
    retriever = get_index().as_retriever(
        filters=metadata_filters,
        image_similarity_top_k=image_similarity_top_k,
        similarity_top_k=text_similarity_top_k,
    )

    query_str = f"""Please return only products that match the following criteria:
{json.dumps(metadata)}"""
    retrieval_results = retriever.retrieve(str_or_query_bundle=query_str)

    filtered_products = {}

    for result in retrieval_results:
        doc_id = result.node.relationships[NodeRelationship.SOURCE].node_id

        if doc_id not in filtered_products:
            filtered_products[doc_id] = {
                "_id": doc_id,
                "classification": result.node.metadata.get("classification"),
                "color": result.node.metadata.get("color"),
                "item_type": result.node.metadata.get("item_type"),
                "materials": result.node.metadata.get("materials"),
                "name": result.node.metadata.get("name"),
                "price": result.node.metadata.get("price"),
                "rating": result.node.metadata.get("rating"),
                "style": result.node.metadata.get("style"),
            }

        if result.node.get_type() == ObjectType.TEXT:
            filtered_products[doc_id]["caption"] = result.node.get_content()

        elif result.node.get_type() == ObjectType.IMAGE:
            filtered_products[doc_id]["image_url"] = result.node.image_url

    return [Product(**product) for product in filtered_products.values()]

def playback_audio(
        text: str,
        voice: Literal['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'] = None,
) -> None:
    """Generate and play audio from the specified text using the specified voice.

    Parameters
    ----------
    text : str
        The text to generate audio from
    voice : Literal['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'], optional
        The voice to use for the audio, by default None

    Returns
    -------
    None
    """
    audio = marvin.speak(
        text=text,
        voice=voice,
    )
    audio.play()
