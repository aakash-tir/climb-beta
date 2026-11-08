import numpy as np
from synth import BLUE, GREEN, ORANGE, RED, YELLOW, draw_hold, tint, wall

from climb_beta.colour.white_balance import apply_gains, grey_world, grey_world_gains


def _neutral_err(img: np.ndarray, region: tuple[slice, slice]) -> float:
    patch = img[region].reshape(-1, 3).astype(float).mean(axis=0)
    return float(patch.max() - patch.min())


def test_restores_warm_tint_on_neutral_wall() -> None:
    img = wall(bgr=(180, 180, 180))
    warm = tint(img, (0.75, 0.95, 1.2))  # warm LED: low blue, high red
    assert _neutral_err(warm, (slice(0, 50), slice(0, 50))) > 50
    fixed = grey_world(warm)
    assert _neutral_err(fixed, (slice(0, 50), slice(0, 50))) < 4


def test_wall_reference_beats_whole_image_when_holds_dominate() -> None:
    img = wall(bgr=(180, 180, 180), h=200, w=200)
    holds = np.zeros((200, 200), dtype=bool)
    # a wall crowded with warm-coloured holds biases a whole-image grey-world
    for i, c in enumerate([RED, ORANGE, YELLOW, RED, ORANGE, GREEN, RED, BLUE, YELLOW]):
        cx, cy = 35 + (i % 3) * 65, 35 + (i // 3) * 65
        holds |= draw_hold(img, (cx, cy), 30, c, seed=i)
    warm = tint(img, (0.8, 1.0, 1.15))
    corner = (slice(0, 4), slice(0, 200))
    whole = grey_world(warm)
    walled = grey_world(warm, ref_mask=~holds)
    assert _neutral_err(walled, corner) < 4
    assert _neutral_err(walled, corner) < _neutral_err(whole, corner)


def test_tiny_reference_falls_back_to_whole_image() -> None:
    img = tint(wall(bgr=(150, 150, 150)), (0.8, 1.0, 1.2))
    ref = np.zeros(img.shape[:2], dtype=bool)
    ref[0, 0] = True
    assert grey_world_gains(img, ref) == grey_world_gains(img)


def test_gains_are_clipped_and_black_image_is_identity() -> None:
    img = np.zeros((20, 20, 3), dtype=np.uint8)
    img[..., 2] = 200  # pure red scene: green/blue means are 0
    assert grey_world_gains(img) == (1.0, 1.0, 1.0)
    img[..., 0] = 10
    img[..., 1] = 10
    g = grey_world_gains(img)
    assert max(g) <= 2.0 and min(g) >= 0.5


def test_apply_gains_saturates() -> None:
    img = np.full((1, 1, 3), 200, dtype=np.uint8)
    assert apply_gains(img, (2.0, 1.0, 0.5))[0, 0].tolist() == [255, 200, 100]
