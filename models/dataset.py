import json


class DataSet:
    def __init__(self, dataframe):

        _exploded_name_df = dataframe.explode(
            "ApplicationProfileName", ignore_index=True
        )
        self.dataframe = self.profile_jsons_to_objs(_exploded_name_df)

        self.exploded_profile_df = self.profile_explode(self.dataframe)

        self._app_profile_names = self._get_app_profile_names(self.exploded_profile_df)
        self._used_lanes = sorted(self.exploded_profile_df["Lane"].unique().tolist())

    def get_profiles_obj(self):
        app_profiles = {}

        for name in self._app_profile_names:
            app_profiles[name] = {}
            app_profiles[name]["Data"] = self.exploded_profile_df[
                self.exploded_profile_df["ApplicationProfileName"] == name
            ]

            profile = app_profiles[name]["Data"]["ApplicationProfile"].iloc[0]

            for field in profile["DataFields"]:
                if field not in app_profiles[name]:
                    app_profiles[name]["Data"][field] = profile["Data"][field]

            app_profiles[name]["Data"] = app_profiles[name]["Data"][
                profile["DataFields"]
            ]
            app_profiles[name]["Settings"] = profile["Settings"]

        return app_profiles

    @property
    def application_profile_names(self):
        return self._app_profile_names

    @property
    def used_lanes(self):
        return self._used_lanes

    def application_profile_by_name(self, profile_name):
        profile_filtered_df = self.exploded_profile_df[
            self.exploded_profile_df["ApplicationProfileName"] == profile_name
        ]

        application_profile = profile_filtered_df["ApplicationProfile"].iloc[0]

        if application_profile:
            return application_profile

        return None

    @staticmethod
    def profile_explode(dataframe):

        def _get_p(profile_name, profile_list):
            for profile in profile_list:
                if profile["ApplicationProfileName"] == profile_name:
                    return profile

            return None

        dataframe = dataframe.explode("ApplicationProfileName", ignore_index=True)

        dataframe["ApplicationProfile"] = dataframe.apply(
            lambda row: _get_p(
                row["ApplicationProfileName"], row["ApplicationProfile"]
            ),
            axis=1,
        )
        return dataframe

    def profile_jsons_to_objs(self, dataframe):
        dataframe["ApplicationProfileName"] = dataframe["ApplicationProfileName"].apply(
            json.loads
        )
        dataframe["ApplicationProfile"] = dataframe["ApplicationProfile"].apply(
            json.loads
        )

        return dataframe

    @staticmethod
    def _exploded_profile_names(dataframe):
        return dataframe.explode("ApplicationProfileName", ignore_index=True)

    @staticmethod
    def _get_app_profile_names(dataframe):
        return sorted(dataframe["ApplicationProfileName"].unique().tolist())
