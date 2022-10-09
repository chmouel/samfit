from .tpsession import do_curl


class TPApi:
    def __init__(self, username: str, token: str, verbose: bool):
        self.verbose = verbose
        self.token = token
        self.username = username

    def get_workouts_from_library(self, library_id: int) -> list:
        return do_curl(
            self.token,
            f"/exerciselibrary/v1/libraries/{library_id}/items",
            cache_id=f"tp_library_{library_id}",
            verbose=self.verbose,
            as_json=True,
        )

    def get_user_info(self) -> dict:
        return do_curl(
            self.token,
            "/users/v3/user",
            cache_id=f"tp_user_{self.username}",
            as_json=True,
            verbose=self.verbose,
        )

    def get_excercise_libraries(self):
        return do_curl(
            self.token,
            "exerciselibrary/v1/libraries",
            cache_id=f"tp_libraries_{self.username}",
            as_json=True,
            verbose=self.verbose,
        )
