from consta.normalizar import cita_existe, normalizar

FUENTE = normalizar("Artículo 12. El proveedor deberá responder el reclamo en un plazo máximo de treinta (30) días hábiles.")


def test_cita_textual_existe_aunque_cambien_tildes_y_espacios():
    assert cita_existe("plazo maximo de   treinta (30) dias", FUENTE)


def test_cita_inventada_no_existe():
    assert not cita_existe("plazo máximo de quince (15) días hábiles", FUENTE)


def test_cita_corta_no_cuenta():
    assert not cita_existe("treinta días", FUENTE)
