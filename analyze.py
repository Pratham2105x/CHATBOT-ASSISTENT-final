import numpy as np

from src.preprocess import classes


cm = np.loadtxt(
    "models/confusion_matrix.csv",
    delimiter=",",
    dtype=int
)

confusions = []

for i in range(len(classes)):
    for j in range(len(classes)):

        if i != j and cm[i, j] > 0:

            confusions.append(
                (
                    cm[i, j],
                    classes[i],
                    classes[j]
                )
            )


confusions.sort(
    reverse=True
)


print("=" * 70)
print("TOP MODEL CONFUSIONS")
print("=" * 70)

for count, actual, predicted in confusions[:20]:

    print(
        f"{count} example(s): "
        f"{actual}  →  {predicted}"
    )

print("=" * 70)