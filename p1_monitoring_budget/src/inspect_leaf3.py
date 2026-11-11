"""Look at the flows in the most suspicious scorer leaf. Prints only, writes nothing."""

from p1_monitoring_budget.src.preprocess import load_clean_data, load_config, split_data
from p1_monitoring_budget.src.sampling import make_strata, train_scorer

# Leaf number of the most suspicious leaf in the scorer tree (seed 0)
LEAF = 3


def main():
    # Load the settings and the data, then split
    config = load_config()
    df = load_clean_data(config)
    train, scorer, test = split_data(df, config)
    columns = config["sampling"]["scorer_features"]

    # Test flows that fall into the leaf
    tree = train_scorer(scorer, config, 0)
    in_leaf = tree.apply(test[columns]) == LEAF
    leaf = test[in_leaf]
    print("flows in leaf", LEAF, ":", len(leaf), "| attacks:", int(leaf["Label"].sum()))
    print()

    # Protocol and destination port of these flows
    print("PROTOCOL (top 10)")
    print(leaf["PROTOCOL"].value_counts().head(10).to_string())
    print()
    print("L4_DST_PORT (top 5)")
    print(leaf["L4_DST_PORT"].value_counts().head(5).to_string())
    print()
    print("IN_BYTES and IN_PKTS in the leaf: min, median, max")
    print(leaf[["IN_BYTES", "IN_PKTS"]].agg(["min", "median", "max"]).to_string())
    print()

    # Strata (protocol plus port class) that contain only attacks
    strata = make_strata(test)
    share = test.groupby(strata)["Label"].mean()
    attack_only = (strata.map(share) == 1.0).to_numpy()

    # How much the leaf and the attack-only strata overlap
    attack = (test["Label"] == 1).to_numpy()
    print("attack flows in the test set:", int(attack.sum()))
    print("attack flows in the leaf:", int((in_leaf & attack).sum()))
    print("flows in attack-only strata:", int(attack_only.sum()))
    print("flows in both the leaf and attack-only strata:", int((in_leaf & attack_only).sum()))
    print("flows in the leaf but not in attack-only strata:", int((in_leaf & ~attack_only).sum()))
    print("flows in attack-only strata but not in the leaf:", int((attack_only & ~in_leaf).sum()))


if __name__ == "__main__":
    main()