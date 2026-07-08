from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SessionVerifyResponse(BaseModel):
    authenticated: bool
    username: str


class RiskSignalRequest(BaseModel):
    symbol: str
    direction: str | None = None
    entry: float
    stop_loss: float
    take_profit: float
    risk_reward: float
    detected_at: str | None = None
    status: str


class ExecuteSignalRequest(BaseModel):
    symbol: str
    direction: str
    entry: float
    stop_loss: float
    take_profit: float
    risk_reward: float
    detected_at: str | None = None
    status: str


class BotConfigRequest(BaseModel):
    execution_mode: str | None = None
    auto_trading_enabled: bool | None = None
