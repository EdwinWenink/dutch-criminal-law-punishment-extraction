from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import kendalltau, rankdata, spearmanr

from src.dataloader import DataLoader
from src.utils import convert_vectors_to_binary

label_names_dutch = ['TBS', 'gevangenis', 'hechtenis', 'taakstraf', 'geldboete', 'vrijspraak']
label_names = ['TBS', 'prison sentence', 'custody', 'community service', 'fine', 'acquittal']

# Show plots and/or save plots?
show = False
save = True
plots_dir = Path('plots/')

# Threshold for significance
p_thresh = 0.05

# Settings
# Global variables
DROP_NAN = True
data_fn = 'parsed_data.csv'
data_dir = 'data/query/'
data_path = data_dir + data_fn
data_key = 'data'
target = 'type'
drop_columns = None
drop_types = ['bijlage', 'overig']

# Initialize data loader
dataloader = DataLoader(data_dir=data_dir,
                        data_key=data_key,
                        target=target,
                        data_fn=data_fn,
                        reduce_to_sentences=False,
                        min_samples_per_class=10)

# Load data
df = dataloader.load(drop_columns=drop_columns,
                     drop_types=drop_types)  # loads data_fn by default

# First do analysis on 'beslissingen' only
beslissingen = df.loc[df['type'] == 'beslissing']
print("N beslissingen: ", len(beslissingen))

# Read out the labels (tuples saved as 'strings') and convert to numpy array
straf_labels = np.array([eval(straf) for straf in beslissingen['straffen']])
straf_labels_bin = convert_vectors_to_binary(straf_labels)
print("Straf labels shape", straf_labels.shape)
print("Max values:", {name: max for name, max in zip(label_names, np.amax(straf_labels, axis=0))})

# Compute basic statistics over straf labels: mean, standard deviation, label cardinality and label density

# Label cardinality: the average number of labels per example in the set
# \frac{1}{N}\sum_{i=1}^N|Y_i|
# Capital Y indicates a label *set* for data sample i
# label_cardinality = np.mean(np.sum(straf_labels.astype(bool), axis=1))
label_cardinality = np.mean(np.sum(straf_labels_bin, axis=1))
print("Label cardinality:", label_cardinality)

# Label density: average over samples of (number of labels *per sample*, divided by total number of labels)
# \frac{1}{N}\sum_{i=1}^N \frac{|Y_i|}{|L|} with L = \union_{i=1}^N Y_i i.e. the total number of available labels
# label_density = np.mean(np.sum(straf_labels.astype(bool), axis=1)/straf_labels.shape[1])
label_density = label_cardinality / straf_labels.shape[1]
print("Label density:", label_density)

# Simple mean and standard deviation
mean_simple = np.mean(straf_labels, axis=0)
std_simple = np.std(straf_labels, axis=0)
print(f"Simple mean and standard deviation:\nMean: {mean_simple}\nStd: {std_simple}")

# Mean and standard deviation for non-zero entries
# N.B. 'where' argument in np.mean is new in numpy 1.20!
# Alternatively, set zeros as nan and then use np.nanmean
mean_nz = np.mean(straf_labels, axis=0, where=(straf_labels > 0))
std_nz = np.std(straf_labels, axis=0, where=(straf_labels > 0))
print(f"Mean and standard deviation of non-zero labels:\nMean: {mean_nz}\nStd: {std_nz}")

# mode is always 0, except for 1 for vrijspraak

# Plot histograms per punishment

# TBS
ax = sns.countplot(x=straf_labels[:, 0])
ax.set_xlabel("No/Yes")
ax.set_ylabel("Counts")
plt.title("Counts for TBS")
plt.tight_layout()
if show:
    plt.show()
if save:
    plt.savefig(plots_dir / 'hist_TBS.png', bbox_inches='tight')
plt.close()

# Gevangenisstraf
ax = sns.histplot(x=straf_labels[:, 1], binrange=(1, max(straf_labels[:, 1])), kde=True)
ax.set_xlabel("Days")
ax.set_ylabel("Counts")
plt.title("Histogram for prison sentence (excl. zero)")
plt.tight_layout()
if show:
    plt.show()
if save:
    plt.savefig(plots_dir / 'hist_prison.png', bbox_inches='tight')
plt.close()

# Hechtenis
ax = sns.histplot(x=straf_labels[:, 2], binwidth=25,
                  binrange=(1, max(straf_labels[:, 2])), kde=True)
ax.set_xlabel("Days")
ax.set_ylabel("Counts")
plt.title("Histogram for custody (excl. zero)")
plt.tight_layout()
if show:
    plt.show()
if save:
    plt.savefig(plots_dir / 'hist_custody.png', bbox_inches='tight')
plt.close()

# Taakstraf
ax = sns.countplot(x=straf_labels[np.nonzero(straf_labels[:, 3])][:, 3])
ax.set_xlabel("Days")
ax.set_ylabel("Counts")
plt.title("Counts for community service (excl. zero)")
plt.tight_layout()
if show:
    plt.show()
if save:
    plt.savefig(plots_dir / 'hist_community_service.png', bbox_inches='tight')
plt.close()

# Geldboete
ax = sns.histplot(x=straf_labels[:, 4], binrange=(1, 900000), kde=True)
ax.set_xlabel("Euros")
ax.set_ylabel("Counts")
plt.title("Histogram for fine (excl. zero)")
plt.tight_layout()
if show:
    plt.show()
if save:
    plt.savefig(plots_dir / 'hist_fine.png', bbox_inches='tight')
plt.close()

# Vrijspraak
ax = sns.countplot(x=straf_labels[:, 5])
ax.set_xlabel("No/Yes")
ax.set_ylabel("Counts")
plt.title("Counts for acquittal")
plt.tight_layout()
if show:
    plt.show()
if save:
    plt.savefig(plots_dir / 'hist_acquittal.png', bbox_inches='tight')
plt.close()

# How many cases are acquittal without other main punishments?
print("Acquittal without other co-occuring punishments.")
# 395/1313 cases with vrijspraak=1
print(np.sum(np.sum(straf_labels[straf_labels[:, 5] == 1], axis=1) == 1))

# CO-OCCURRENCE MATRIX

# Which combinations of punishments are most common?
# Compute co-occurrence matrix of punishments
co_occurrence = np.dot(straf_labels_bin.T, straf_labels_bin)
print("Co-occurrence matrix:\n", co_occurrence)

diagonal = np.diagonal(co_occurrence)
assert np.sum(diagonal) == np.sum(straf_labels_bin)
print("Total punishments assigned in all cases:", np.sum(diagonal))

label_names = ['TBS', 'prison sentence', 'custody',
               'community service', 'fine', 'acquittal']

cmap = sns.diverging_palette(20, 230, as_cmap=True)
ax = sns.heatmap(co_occurrence,
                 cmap=cmap,
                 annot=True, xticklabels=label_names,
                 fmt='g',  # do not use scientific notation
                 yticklabels=label_names, center=0, square=True, linewidth=.5)
plt.title("Co-occurrence matrix of punishments.")
plt.tight_layout()
if show:
    plt.show()
if save:
    plt.savefig(plots_dir / 'co_occurrence.png', bbox_inches='tight')
plt.close()

# Normalize co-occurrence matrix entries i,j by popularity of i and j
# i.e. (i and j) / (i or j) -> This is effectively the Jaccard similarity!
co_occurrence_norm = np.zeros(co_occurrence.shape)
for i in range(co_occurrence.shape[0]):
    for j in range(co_occurrence.shape[1]):
        if i == j:
            union = diagonal[i]
        else:
            union = diagonal[i] + diagonal[j] - co_occurrence[i, j]
        # denom = np.sum(co_occurrence[i]) + np.sum(co_occurrence[j]) - co_occurrence[i, j]
        jaccard = co_occurrence[i, j] / union
        co_occurrence_norm[i, j] = jaccard

print("Co-occurrence matrix normalized by popularity:\n", co_occurrence_norm)

cmap = sns.diverging_palette(20, 230, as_cmap=True)
ax = sns.heatmap(co_occurrence_norm,
                 cmap=cmap,
                 annot=True, xticklabels=label_names,
                 # fmt='.3f',  # do not use scientific notation
                 yticklabels=label_names, center=0, square=True, linewidth=.5)
plt.title("Co-occurrence matrix of punishments normalized by popularity (Jaccard index).")
plt.tight_layout()
if show:
    plt.show()
if save:
    plt.savefig(plots_dir / 'co_occurrence_norm.png', bbox_inches='tight')
plt.close()

tbs = straf_labels[:, 0]
gevangenis = straf_labels[:, 1]
hechtenis = straf_labels[:, 2]
taakstraf = straf_labels[:, 3]
boete = straf_labels[:, 4]
vrijspraak = straf_labels[:, 5]

# EXP 1: Correlation between labels themselves
'''
We have a multi-output problem, where each output is either the height or a binary value indicating presence.
One approach to tackling this kind of problem is to decompose this into multiple single-output problems.
Decomposing this in multiple single-output problems ignores that the outputs themselves may be correlated.
So we should start with an analysis of the correlation between labels.
We expect there to be correlation: e.g. a community service is often accompanied by a fine.
'''

# Compute the correlation matrix indicating Pearson correlation coefficients
# This function somewhat atypically assumes that rows indicate variables and columns observations
# We transpose this interpretation with rowvar=False
# See: https://numpy.org/doc/stable/reference/generated/numpy.corrcoef.html
# See: https://numpy.org/doc/stable/reference/generated/numpy.cov.html#numpy.cov
corr_matrix = np.corrcoef(straf_labels, rowvar=False)

# Spearman's Rho is often used on continuous data when it has outliers (this holds in our case)
spearman_corr, spearman_p = spearmanr(straf_labels, axis=0)
print("Spearman Correlation on continuous labels:\n", spearman_corr)
print("p-values:\n", spearman_p)

# Check how many p-values do not meet the chosen significance threshold
triangle_mask = np.triu(np.ones_like(spearman_corr, dtype=bool))
insignificant_mask = spearman_p[triangle_mask] > p_thresh
n_insignificant = sum(insignificant_mask)
if n_insignificant == 0:
    print("All correlation coefficients are statistically significant")
else:
    print(f"WARNING: {n_insignificant} coefficients are insignificant with p={p_thresh}")

# Double check: Spearmans' rho is in fact the Pearson correlation on the ranks of the data
ranks = rankdata(straf_labels, axis=0)
spearman_check = np.corrcoef(ranks, rowvar=False)
np.testing.assert_almost_equal(spearman_check, spearman_corr, decimal=7)

# Mask to remove upper triangle
triangle = False
if triangle:
    mask = triangle_mask
else:
    mask = np.zeros_like(spearman_corr, dtype=bool)

# Visualize Spearman's correlation as a heatmap
cmap = sns.diverging_palette(20, 230, as_cmap=True)
ax = sns.heatmap(spearman_corr, mask=mask, cmap=cmap, annot=True, xticklabels=label_names,
                 yticklabels=label_names, center=0, square=True, linewidth=.5)
plt.title("Spearman's Rho on continuous punishment labels")
plt.tight_layout()
if show:
    plt.show()
plt.close()

# Repeat analysis on binary version of the labels
spearman_corr_bin, spearman_p_bin = spearmanr(straf_labels_bin)
print("Spearman Correlation on binary labels:\n", spearman_corr_bin)
print("p-values:\n", spearman_p_bin)

insignificant_mask = spearman_p_bin[triangle_mask] > p_thresh
n_insignificant_bin = sum(insignificant_mask)
if n_insignificant_bin == 0:
    print("All correlation coefficients are statistically significant")
else:
    print(f"WARNING: {n_insignificant_bin} coefficients are insignificant with p={p_thresh}")

# Visualize on binary labels
ax = sns.heatmap(spearman_corr_bin, mask=mask, cmap=cmap, annot=True, xticklabels=label_names,
                 yticklabels=label_names, center=0, square=True, linewidth=.5)

plt.title("Spearman's Rho on binary punishment labels")
ax.figure.tight_layout()
if show:
    plt.show()
plt.close()

# PAIRWISE CORRELATIONS ON NON-ZERO PAIRS
# ---------------------------------------

# NOTE this 'method' does not work for TBS and vrijspraak
# the > 0 filter will give a constant array
# i.e. a degenerate case with only tied ranks

# GEVANGENIS

# Correlation in situations where both gevangenisstraf and hechtenis are assigned
mask = np.logical_and(gevangenis > 0, hechtenis > 0)
print("gevangenis x hechtenis co-occurence")
print("N =", len(gevangenis[mask]))
spearman_corr, spearman_p = spearmanr(np.vstack((gevangenis[mask], hechtenis[mask])), axis=1)
print(spearman_corr)  # 0.18
print(spearman_p)  # p=0.55
print()

# Correlation in situations where both gevangenisstraf and boete are assigned
mask = np.logical_and(gevangenis > 0, boete > 0)
print("gevangenis x fine co-occurence")
print("N =", len(gevangenis[mask]))
spearman_corr, spearman_p = spearmanr(np.vstack((gevangenis[mask], boete[mask])), axis=1)
print(spearman_corr)  # 0.32
print( spearman_p)  # p=6.62 e-0.8
print()

# Correlation in situations where both gevangenisstraf and taakstraf are assigned
mask = np.logical_and(gevangenis > 0, taakstraf > 0)
print("gevangenis x taakstraf co-occurence")
print("N =", len(gevangenis[mask]))
spearman_corr, spearman_p = spearmanr(np.vstack((gevangenis[mask], taakstraf[mask])), axis=1)
print(spearman_corr)  # 0.34
print(spearman_p)  # p=1.43 e-08
print()

# HECHTENIS

# Correlation in situations where both hechtenis and boete are assigned
mask = np.logical_and(hechtenis > 0, boete > 0)
print("custody x fine co-occurence")
print("N =", sum(mask))
spearman_corr, spearman_p = spearmanr(np.vstack((hechtenis[mask], boete[mask])), axis=1)
print(spearman_corr)  # .41
print(spearman_p)  # 0.00263
print()

# Correlation in situations where both hechtenis and taakstraf are assigned
mask = np.logical_and(hechtenis > 0, taakstraf > 0)
print("hechtenis x taakstraf co-occurence")
print("N =", sum(mask))
spearman_corr, spearman_p = spearmanr(np.vstack((hechtenis[mask], taakstraf[mask])), axis=1)
print(spearman_corr)  # -0.0059
print(spearman_p)  # .97
print()

# TAAKSTRAF
# Correlation in situations where both taakstraf and boete are assigned
mask = np.logical_and(taakstraf > 0, boete > 0)
print("taakstraf x boete co-occurence")
print("N =", sum(mask))
spearman_corr, spearman_p = spearmanr(np.vstack((taakstraf[mask], boete[mask])), axis=1)
print(spearman_corr)  # .25
print(spearman_p)  # p=0.00739
print()

# Plot results of manual evaluation (hard coded)

# Results from manual evaluation in paper
TP, FN, TN, FP = 45, 5, 52, 5
data = [[TP, FN],
        [FP, TN]]

# Define labels
labels = ['Sentence', 'No sentence']

# Create confusion matrix with Seaborn heatmap
cmap = sns.diverging_palette(20, 230, as_cmap=True)
sns.set(color_codes=True)
sns.set(font_scale=1.2)
plt.figure(1, figsize=(9, 6))
plt.title("Confusion matrix (35 cases)")

ax = sns.heatmap(data, annot=True, cmap=cmap,
                 center=0, square=True, linewidth=.5)
ax.set_xticklabels(labels)
ax.set_yticklabels(labels)
ax.set(ylabel="True Label", xlabel="Predicted Label")

plt.tight_layout()
if save:
    plt.savefig(plots_dir / 'confusion_matrix.png', bbox_inches='tight', dpi=300)
if show:
    plt.show()
plt.close()
