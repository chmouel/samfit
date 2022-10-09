import datetime

from samfit.config import TP_TYPE_REV
from .tpsession import do_curl


class TPApi:
    def __init__(self, username: str, token: str, verbose: bool):
        self.verbose = verbose
        self.token = token
        self.username = username

    def get_workouts_from_library(self, library_name: str) -> (int | list):
        exerciselibrary_dict = self.get_excercise_libraries()
        libraries = [
            x["exerciseLibraryId"]
            for x in exerciselibrary_dict
            if x["libraryName"] == library_name
        ]
        if not libraries:
            raise Exception(
                f"TP library name '{library_name}' could not be found: {exerciselibrary_dict}"
            )

        library_id = libraries[0]
        if self.verbose:
            print(f"Library Name and ID: {library_name} {library_id}")
        return library_id, do_curl(
            self.token,
            f"/exerciselibrary/v1/libraries/{library_id}/items",
            cache_id=f"tp_library_{library_id}",
            verbose=self.verbose,
            as_json=True,
        )

    def create_calendar_note(
        self,
        banner_message: str,
        athlete_id: int,
        date: datetime.datetime,
        name: str,
        title: str,
        coachComment: str,
        description: str,
        test: bool = False,
    ):
        dico = {
            "athleteId": athlete_id,
            "workoutDay": date.strftime("%Y-%m-%d"),
            "title": title,
            "workoutTypeValueId": TP_TYPE_REV["Cycling"],
            "description": description,
            "coachComments": coachComment,
            "completed": False,
            "publicSettingValue": 0,
            "personalRecordCount": 0,
        }
        if test:
            print(dico)
        else:
            do_curl(
                self.token,
                f"/fitness/v3/athletes/{athlete_id}/workouts",
                method="POST",
                verbose=self.verbose,
                data=dico,
            ).decode("utf-8")
        print(
            f"{banner_message}: '{name}' on {date.strftime('%a %Y-%b-%d')} has been created"
        )

    def get_user_info(self) -> dict:
        return do_curl(
            self.token,
            "/users/v3/user",
            cache_id=f"tp_user_{self.username}",
            as_json=True,
            verbose=self.verbose,
        )

    def create_calendar_workout_from_library(
        self,
        name: str,
        athlete_id: int,
        exerciseLibraryItemId: int,
        date: int,
        test: bool = False,
    ) -> None:
        jeez = {
            "athleteId": athlete_id,
            "exerciseLibraryItemId": exerciseLibraryItemId,
            "workoutDateTime": date.strftime("%Y-%m-%d"),
        }
        if test:
            print(jeez)
        else:
            do_curl(
                self.token,
                f"/fitness/v1/athletes/{athlete_id}/commands/addworkoutfromlibraryitem",
                method="POST",
                verbose=self.verbose,
                data=jeez,
            ).decode("utf-8")

        print(f"Workout: '{name}' on {date.strftime('%a %Y-%b-%d')} created")

    def get_excercise_libraries(self):
        return do_curl(
            self.token,
            "exerciselibrary/v1/libraries",
            cache_id=f"tp_libraries_{self.username}",
            as_json=True,
            verbose=self.verbose,
        )
