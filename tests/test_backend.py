from PIL import Image

from services.flashlight_scenarios import ScenarioManager
from utils.image_mapper import ImageMapper


def test_seats_loaded(seats_loader):
    stats = seats_loader.get_stats()
    assert stats["total_seats"] > 0
    assert set(seats_loader.get_all_tribunes()) == {"A", "C", "K", "S"}


def test_image_mapper_fill_rate(seats_loader):
    w, h = seats_loader.get_arena_dimensions()
    mapper = ImageMapper(seats_loader.all_seats, w + 1, h + 1)
    colors = mapper.map_image_to_seats(Image.new("RGB", (50, 50), (255, 0, 0)), 0.5)
    assert 0 < len(colors) <= len(seats_loader.all_seats) * 0.5 + 1


def test_every_scenario_produces_frames(seats_loader):
    w, h = seats_loader.get_arena_dimensions()
    seats = seats_loader.all_seats
    params = {"text_scroll": {"text": "CSKA"}}
    for item in ScenarioManager.list_scenarios():
        sc = ScenarioManager.create_scenario(item["id"], seats, w, h, **params.get(item["id"], {}))
        frame = sc.generate_frame(0, 10)
        assert isinstance(frame, dict)


def test_api_health_and_library(client):
    assert client.get("/health").json() == {"status": "ok"}
    images = client.get("/api/images/library").json()["images"]
    assert len(images) > 0


def test_api_generate_image(client):
    image_id = client.get("/api/images/library").json()["images"][0]["id"]
    r = client.post("/api/images/generate", json={"image_id": image_id, "fill_rate": 0.8})
    assert r.status_code == 200
    assert r.json()["success"] is True


def test_api_flashlight_wave(client):
    r = client.post("/api/flashlights/generate", json={"scenario": "wave", "frames": 3})
    assert r.status_code == 200
    assert len(r.json()["frames"]) == 3
