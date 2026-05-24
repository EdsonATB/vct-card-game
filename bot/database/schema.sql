CREATE TABLE IF NOT EXISTS jogadores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    jogo VARCHAR(50) NOT NULL DEFAULT 'valorant',
    time_atual VARCHAR(100),
    imagem_url TEXT,
    total_claims INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS usuarios (
    discord_id BIGINT PRIMARY KEY,
    moedas INT NOT NULL DEFAULT 0,
    ultimo_roll TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW() - INTERVAL '1 hour'
);

CREATE TABLE IF NOT EXISTS inventario (
    id SERIAL PRIMARY KEY,
    id_usuario BIGINT NOT NULL REFERENCES usuarios(discord_id) ON DELETE CASCADE,
    id_jogador INT NOT NULL REFERENCES jogadores(id) ON DELETE CASCADE,
    data_claim TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_inventario_usuario ON inventario(id_usuario);
CREATE INDEX IF NOT EXISTS idx_inventario_jogador ON inventario(id_jogador);
