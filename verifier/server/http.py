from verifications.discord import start_discord
from verifications.twitter import start_twitter
from verifications.github import start_github
from verifications.utils import str_to_felt
from verifications.common import generate_signature
from aiohttp import web
import aiohttp_cors
import traceback
import time


class WebServer:
    def __init__(self, conf) -> None:
        self.conf = conf

    async def sign(self, request):
        params = await request.json()
        verif_type = params["type"]
        token_id = int(params["token_id"])
        timestamp = int(time.time()) + 3600

        if verif_type not in ["discord", "twitter", "github"]:
            return web.json_response({"status": "error", "error": "invalid type"})

        if verif_type == "discord":
            code = params["code"]
            try:
                user_id, username, discriminator = await start_discord(self.conf, code)
                (sign0, sign1) = generate_signature(
                    token_id,
                    timestamp,
                    28263441981469284,
                    int(user_id),
                    self.conf.verifier_key,
                )
                return web.json_response(
                    {
                        "status": "success",
                        "timestamp": timestamp,
                        "user_id": user_id,
                        "username": username,
                        "discriminator": discriminator,
                        "sign0": str(hex(sign0)),
                        "sign1": str(hex(sign1)),
                    }
                )
            except Exception:
                print(traceback.format_exc())
                return web.json_response(
                    {"status": "error", "error": "unable to query discord data"}
                )

        elif verif_type == "twitter":
            code = params["code"]
            try:
                user_id, username, name = await start_twitter(self.conf, code)
                (sign0, sign1) = generate_signature(
                    token_id,
                    timestamp,
                    32782392107492722,
                    int(user_id),
                    self.conf.verifier_key,
                )
                return web.json_response(
                    {
                        "status": "success",
                        "timestamp": timestamp,
                        "user_id": user_id,
                        "username": username,
                        "name": name,
                        "sign0": str(hex(sign0)),
                        "sign1": str(hex(sign1)),
                    }
                )
            except Exception:
                print(traceback.format_exc())
                return web.json_response(
                    {"status": "error", "error": "unable to query twitter data"}
                )
        elif verif_type == "github":
            try:
                code = params["code"]
                user_id, username, name = await start_github(self.conf, code)
                (sign0, sign1) = generate_signature(
                    token_id,
                    timestamp,
                    113702622229858,
                    user_id,
                    self.conf.verifier_key,
                )
                return web.json_response(
                    {
                        "status": "success",
                        "timestamp": timestamp,
                        "user_id": user_id,
                        "username": username,
                        "name": name,
                        "sign0": str(hex(sign0)),
                        "sign1": str(hex(sign1)),
                    }
                )
            except Exception:
                print(traceback.format_exc())
                return web.json_response(
                    {"status": "error", "error": "unable to query github data"}
                )

    def build_app(self):
        app = web.Application()
        app.add_routes([web.post("/sign", self.sign)])
        cors = aiohttp_cors.setup(
            app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                )
            },
        )
        for route in list(app.router.routes()):
            cors.add(route)
        return app
