from pydantic import BaseModel

class MovieFormData(BaseModel):
    order_by: str | None = "Rating"
    genres: list[str] | None = []
    rating_min: float | None = 0.0
    rating_max: float | None = 0.0
    count_slider_min: float | None = 0.0
    count_slider_max: float | None = 0.0
    items_per_page: int  | None = 10
    movie_title: str | None = ""