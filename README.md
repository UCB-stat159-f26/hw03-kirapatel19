# Tennis Career

A Python package for retrieving tennis match data from Tennis Abstract and plotting a player's age against their age difference with opponents.

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/UCB-stat159-f26/hw03-kirapatel19.git
```

This repository is private, so installation requires GitHub access
to the repository.

For development, run these commands inside the cloned repository:

```bash
python -m pip install -e ".[test]"
```

## Usage

```python
import matplotlib.pyplot as plt
from tennis_career import get_player_matches, plot_age_difference

serena = get_player_matches("serena williams")
plot_age_difference(serena)
plt.show()

rafa = get_player_matches("Rafael Nadal")
plot_age_difference(rafa)
plt.show()
```

Names like `"serena williams"`, `"Serena Williams"`, and
`"SerenaWilliams"` are supported. For names without spaces,preserve the capitalization used by Tennis Abstract.

An invalid player name produces an error:

```python
get_player_matches("GastonSanchez")
```

## Functions

### get_player_matches(player_name)

Downloads the player's profile and Career.js file from Tennis Abstract and returns a cleaned pandas DataFrame containing:

- `match_date`
- `result`: W or L
- `opponent`
- `opponent_age`
- `player_age`
- `age_difference`: player age minus opponent age

Player birth dates come from profile pages. Opponent birth dates are converted to ages when provided; numeric opponent ages are used directly.
Calculated ages use elapsed days divided by 365.25.

Rows missing dates or ages needed for plotting are removed.
Only rows with W or L results are retained. Coverage depends on the records available in Tennis Abstract's Career.js files.

### plot_age_difference(matches)

Takes the cleaned DataFrame and returns a Matplotlib Axes object.

The x-axis shows player age, and the y-axis shows player age minus opponent age. Points are colored by win or loss. Positive differences
mean the player was older than the opponent.

## Tests

Run the automated tests from the repository folder:

```bash
python -m pytest -q
```

The tests use mock JavaScript content and do not contact live servers.
They check match extraction, female and male age calculations, and missing or malformed match data.

## Personal Reflections

This assignment helped me understand how to turn the work from HW2 into functions that someone else can use. I had to think about more
than just Serena because the female and male data store opponent ages differently. Splitting the work into smaller functions made it easier
to understand what each part was doing.

The tests were especially useful because the female age test caught an error where pandas was trying to store decimal ages as whole
numbers. Changing the column to allow decimals fixed the issue.
I also learned how pyproject.toml makes the package installable and how __init__.py makes the main functions available to users.