"""Build the three baseline models from the settings in p1.yaml."""

from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def build_model(name, config, seed):
    # Read the settings for this model and the class weight
    params = config["models"][name]
    weight = config["training"]["class_weight"]

    if name == "logreg":
        # Scale the features first, because logistic regression needs it
        return make_pipeline(
            StandardScaler(),
            LogisticRegression(class_weight=weight, random_state=seed, **params),
        )

    if name == "random_forest":
        return RandomForestClassifier(class_weight=weight, random_state=seed, **params)

    if name == "lightgbm":
        # verbose=-1 hides the training messages
        return LGBMClassifier(class_weight=weight, random_state=seed, verbose=-1, **params)

    raise ValueError(f"Unknown model name: {name}")