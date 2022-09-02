import logging
import warnings
import functools
import difflib
from typing import Sequence
from omegaconf import DictConfig, OmegaConf
import rich
from rich.syntax import Syntax
from rich.tree import Tree
from sklearn.decomposition import TruncatedSVD, PCA
from sklearn.metrics import calinski_harabasz_score, silhouette_score, silhouette_samples
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.pipeline import make_pipeline
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
from matplotlib.colors import rgb2hex
import numpy as np
import pandas as pd
from ast import literal_eval
from scipy import sparse
import seaborn as sns
# import plotly.graph_objs as go
import plotly.express as px
from yellowbrick.cluster import KElbowVisualizer
from sklearn.preprocessing import Normalizer


def get_logger(name=__name__, level=logging.INFO):
    """Initializes python logger."""

    logger = logging.getLogger(name)
    logger.setLevel(level)

    return logger


# Initialize logger that can be used by other util functions
log = get_logger(__name__)


def construct_ECLI_query(params: dict):
    '''
    This function helps construct a query that can be passed
    to the rechtspraak.nl RESTful API. This is done by providing
    the query as constructed here to the CaseLoader class.

    params:     the keys of this dictionary must correspond to keys
                accepted by the rechtspraak.nl API
    '''

    # Er is een "proceduresoort" parameter, maar zo te zien niet voor het bevragen van de ECLI index

    # Construct query
    components = []
    for key, value in params.items():
        # The ECLI query processing two identically names 'data' keys
        # We can't use duplicate keys in dicts, so we stored them as
        # date_from and date_until and then postprocessing the key here
        if 'date' in key:
            key = key.split('_')[0]
        components.append(f"{key}={value}")

    # Components are joined by '&' sign
    query = '&'.join(components)

    log.info(f"Query: {query}")

    return query


def extras(config: DictConfig) -> None:
    """A couple of optional utilities for OmegaConf
    These extras are controlled by the main config file:
        - disabling warnings
        - easier access to debug mode
        - forcing debug friendly configuration
        - forcing multi-gpu friendly configuration
    Args:
        config (DictConfig): [description]
    """
    # enable adding new keys to config
    OmegaConf.set_struct(config, False)

    # disable python warnings if <config.ignore_warnings=True>
    if config.get("ignore_warnings"):
        log.info(f"Disabling python warnings! <config.ignore_warnings=True>")
        warnings.filterwarnings("ignore")

    # set <config.trainer.fast_dev_run=True> if <config.debug=True>
    if config.get("debug"):
        log.info("Running in debug mode! <config.debug=True>")
        #config.trainer.fast_dev_run = True

    # disable adding new keys to config
    OmegaConf.set_struct(config, True)


def print_config(
        config: DictConfig,
        fields: Sequence[str] = (
                "features"
        ),
        resolve: bool = True) -> None:
    """Prints content of DictConfig using Rich library and its tree structure.
    Args:
        config (DictConfig): Config.
        fields (Sequence[str], optional): Determines which main fields from config will be printed
        and in what order.
        resolve (bool, optional): Whether to resolve reference fields of DictConfig.
    """

    style = "dim"
    tree = Tree(":gear: CONFIG", style=style, guide_style=style)

    for field in fields:
        branch = tree.add(field, style=style, guide_style=style)

        config_section = config.get(field)
        branch_content = str(config_section)
        if isinstance(config_section, DictConfig):
            branch_content = OmegaConf.to_yaml(config_section, resolve=resolve)

        branch.add(Syntax(branch_content, "yaml"))

    rich.print(tree)


def compose(*functions):
    '''
    Compose an arbitary amount of functions into a single function
    Source: https://mathieularose.com/function-composition-in-python
    '''
    def comp(f, g):
        return lambda x: f(g(x))
    return functools.reduce(comp, functions, lambda x: x)


def principal_components(X, n_components, plot_dir='plots', run_name='default', seed=None):
    '''
    Apply PCA on feature matrix X. If input data is sparse, it will be converted
    to dense representation because PCA requires this (unlike SVD).

    It is *assumed* that feature scaling is already performed prior to calling this function!
    '''

    if sparse.issparse(X):
        X = X.todense()

    pca = PCA(n_components, random_state=seed)
    X = pca.fit_transform(X)

    # Plot cumulative explained variance against N PCA components
    plt.plot(pca.explained_variance_ratio_.cumsum(), lw=2)
    plt.title('Cumulative variance explained variance by N components', size=15)
    plt.savefig(f"{plot_dir}/{run_name}-pca_cum_variance.png", format='png')
    plt.show()
    plt.clf()

    # Report total explained variance
    var_coverage = pca.explained_variance_ratio_.sum()
    log.info(f"PCA Total explained variance: {int(var_coverage*100)}%")

    return X, pca


def SVD(X, n_components, plot_dir='plots', run_name='default', seed=None):
    '''
    Apply SVD on feature matrix X.
    It is *assumed* that feature scaling is already performed prior to calling this function!
    '''

    svd = TruncatedSVD(n_components, random_state=seed)
    X = svd.fit_transform(X)

    # Plot cumulative explained variance against N components
    plt.plot(svd.explained_variance_ratio_.cumsum(), lw=2)
    plt.title('Cumulative explained variance by N components', size=15)
    plt.savefig(f"{plot_dir}/{run_name}-svd_cum_variance.png", format='png')
    plt.tight_layout()
    plt.show()
    plt.clf()

    # Report total explained variance
    var_coverage = svd.explained_variance_ratio_.sum()
    print(f"SVD Total explained variance: {int(var_coverage*100)}%")
    return X, svd


def T_SNE(X, n_components, plot_dir='plots', run_name='default', seed=None):
    # n components must be <4?
    X = TSNE(n_components, init='pca', verbose=1, perplexity=20, n_iter=1000, learning_rate=200.0, random_state=seed).fit_transform(X)
    return X


def LSA(X, n_components, plot_dir='plots', run_name='default', seed=None):
    svd = TruncatedSVD(n_components, random_state=seed)
    normalizer = Normalizer(copy=False)
    lsa = make_pipeline(svd, normalizer)

    X = lsa.fit_transform(X)

    # Plot cumulative explained variance against N PCA components
    plt.plot(svd.explained_variance_ratio_.cumsum(), lw=2)
    plt.title('Cumulative variance explained variance by N components', size=15)
    plt.savefig(f"{plot_dir}/{run_name}-lsa_cum_variance.png", format='png')
    plt.show()
    plt.clf()

    # Report total explained variance
    var_coverage = svd.explained_variance_ratio_.sum()
    log.info(f"LSA Total explained variance: {int(var_coverage*100)}%")
    print(f"LSA Total explained variance: {int(var_coverage*100)}%")
    return X, svd


def compute_loadings(pca, feature_names) -> pd.DataFrame:
    '''
    Computes the 'loadings' of principal components
    Also works with PCA

    pca:            fitted pca or svd object
    feature_names   names of features before dimensionality reduction

    returns
    '''
    loadings = pd.DataFrame(
            data=pca.components_.T * np.sqrt(pca.explained_variance_),
            columns=[f'PC{i}' for i in range(1, len(pca.components_)+1)],
            index=feature_names
    )
    return loadings


def vis_load_for_PC(pc_number, loadings, k=20, plot_dir='plots', run_name='default'):
    '''
    Show top-k features most correlated with principle component of pc_number
    Show both top k most positive and negative  correlations
    '''
    mpl.rcParams.update(mpl.rcParamsDefault)

    id = f'PC{pc_number}'
    loading = loadings.sort_values(by=id, ascending=False)[id]
    loading = loading.reset_index()
    loading.columns = ['Feature', 'Correlation']

    # Top k most positively correlated features
    plt.bar(loading['Feature'][:k], loading['Correlation'][:k])
    plt.title(f'Top {k} most positively correlated features for {id}')
    plt.xticks(rotation='vertical')
    plt.tight_layout()
    plt.savefig(f"{plot_dir}/{run_name}-pos_cor_features_{id}.png", format='png')
    plt.show()
    plt.clf()

    # Top k most negatively correlated features
    plt.bar(loading['Feature'][-k:], loading['Correlation'][-k:])
    plt.title(f'Top {k} most negatively correlated features for {id}')
    plt.xticks(rotation='vertical')
    plt.tight_layout()
    plt.savefig(f"{plot_dir}/{run_name}-neg_cor_features_{id}.png", format='png')
    plt.show()
    plt.clf()


def visualize_clusters(X, labels, n_clusters, method='svd', dim=3, symbol=None, hover=None, title=None, seed=42):
    '''
    dim:                whether to visualize in 2D or 3D
    symbol (Optional):  column name in df (str, int) or sequence of labels (Series, array-like) to assign mark symbols
    hover:              additional data to show when hovering over data points;
                        provide as column names in X or dict {'new key': hover_data}
    '''

    # TODO use select_dimensionality_reduction method from this class for brevity?

    if method == 't-sne':
        # Notice n_components is dim and not hardcoded as 3 (diff with PCA and SVD);
        # t-SNE is a visualization firstly, dimensionality reduction technique only secondly
        reduction = TSNE(n_components=dim,
                         init='pca',
                         verbose=1,
                         perplexity=20,  # NOTE This parameter must be experimentally for each new data set
                         n_iter=5000,
                         learning_rate=200.0,
                         random_stat=seed).fit_transform(X)
    elif method == 'svd':
        dimred = TruncatedSVD(n_components=3, random_state=seed)
    else:
        # PCA is a good default
        dimred = PCA(n_components=3, random_state=seed)

    reduction = dimred.fit_transform(X)

    print(f"Dimensionality reduction for visualization captured {int(dimred.explained_variance_ratio_.sum()*100)} variance")

    if title is None:
        title = f"{method}-reduced data"

    # Convert labels to string to force them being treated as categorical
    if not isinstance(labels[0], int):
        labels = [str(label) for label in labels]

    if dim == 2:
        # NOTE currently does not have a hover effect like the 3D plot
        # (because this is not an interactive plot by default)
        # n_categories = 17
        # palette = sns.color_palette("hls", n_colors=n_categories)
        plt.figure(figsize=(10, 10))
        sns.scatterplot(x=reduction[:, 0], y=reduction[:, 1],
                        hue=labels,
                        style=symbol,
                        # palette=palette,
                        palette='tab20',  # Make sure this colormap has enough categories!
                        s=100,
                        alpha=0.8).set_title(title)

        # Legend tends to overlap with the clusters, so shift legend to right
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1))
        plt.xlabel('Component 1')
        plt.ylabel('Component 2')
        plt.tight_layout()
        plt.show()
    elif dim == 3:
        # N.B. this opens in a browser
        '''
        scene = dict(xaxis=dict(title='PC1'), yaxis=dict(title='PC2'), zaxis=dict(title='PC3'))
        trace = go.Scatter3d(x=reduction[:, 0], y=reduction[:, 1], z=reduction[:, 2],
                             mode='markers',
                             marker=dict(color=labels, colorscale='Viridis', size=10, line=dict(color='gray', width=5)))
        layout = go.Layout(margin=dict(l=0, r=0),
                           showlegend=True,
                           scene=scene,
                           height=1000,
                           width=1000)
        fig = go.Figure(data=[trace], layout=layout)
        fig.show()
        '''

        # Get the same colorpalette 'tab20' as above
        # But plotly express expects CSS hex values
        # so we need to manually convert the colormap

        cmap = cm.get_cmap('tab20')
        color_sequence_hex = [rgb2hex(cmap(i)) for i in range(cmap.N)]

        fig = px.scatter_3d(reduction, x=0, y=1, z=2,
                            color=labels,
                            color_discrete_sequence=color_sequence_hex,
                            opacity=1,
                            labels={'0': 'Component 1', '1': 'Component 2', '2': 'Component 3'},
                            symbol=symbol,
                            hover_data=hover,
                            title=title)

        # TODO When symbol is specified, I'd like to have two legend entries for the two groups
        # But this is currently not supported in plotly. See https://github.com/plotly/plotly.js/issues/5099

        # Modify positon of legend
        fig.update_layout(legend=dict(
                              yanchor="top",
                              y=0.7,
                              xanchor="right",
                              x=0.95),
                          title=dict(
                              yanchor='top',
                              y=0.9,
                              xanchor='center',
                              x=0.5))  # margin=dict(l=0, r=0, b=0, t=0),

        # Update styling of traces
        fig.update_traces(marker=dict(
                            # colorscale='Viridis',
                            size=10,
                            line=dict(color='gray', width=1)))
        fig.show()
    else:
        print("Warning: either select 2D or 3D (dim=2 or dim=3)")


def select_dimensionality_reduction(X, reduction_method=None, n_components=3, run_name='default', seed=42):
    '''
    Helper function that applies either 'pca', 'svd' or 't-sne'
    '''
    if reduction_method is None:
        print("No dimensionality reduction selected")
        return X
    elif reduction_method.lower() == 'pca':
        X, pca = principal_components(X, n_components, plot_dir='plots', run_name=run_name, seed=seed)
        print("Reduction: Principal Component Analysis (PCA)")
        print(f"PCA total explained variance: {int(pca.explained_variance_ratio_.sum()*100)}%")
    elif reduction_method.lower() == 'svd':
        X, svd = SVD(X, n_components, plot_dir='plots', run_name=run_name, seed=seed)
        print("Reduction: Singular Value Decomposition (SVD)")
        print(f"SVD total explained variance: {int(svd.explained_variance_ratio_.sum()*100)}%")
    elif reduction_method.lower() == 't-sne':
        # note n_components should be <4 so n_components parameter is not used
        print("Reduction: t-SNE")
        print("Warning: t-sne does not use the provided n_components parameter")
        X = T_SNE(X, n_components=3, plot_dir='plots', run_name=run_name, seed=seed)
    elif reduction_method.lower() == 'lsa':
        print("Reduction: performing Latent Semantic Analysis (LSA) ")
        X = LSA(X, n_components, plot_dir='plots', run_name=run_name, seed=seed)
    else:
        print("No dimensionality reduction selected")
    return X


def visualize_decision_boundary_clusters_2D(X, n_clusters, plot_dir='plots', method='svd'):
    '''
    Visualizes clusters with decision boundaries

    Code adapted from here: https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_digits.html
    Adapted to also use SVD, because PCA does not work on sparse input matrices
    '''

    if method.lower() == 'pca':
        # PCA does not work with sparse data
        if sparse.issparse(X):
            log.info("PCA does not work with sparse matrices. Converting to dense representation.")
            X = X.todense()
        pca = PCA(n_components=2)
        reduced_data = pca.fit_transform(X)
    else:
        svd = TruncatedSVD(n_components=2)
        reduced_data = svd.fit_transform(X)

    kmeans = KMeans(init="k-means++", n_clusters=n_clusters, n_init=10)
    kmeans.fit(reduced_data)

    # Step size of the mesh. Decrease to increase the quality of the VQ.
    h = .02     # point in the mesh [x_min, x_max]x[y_min, y_max].

    # Plot the decision boundary. For that, we will assign a color to each
    x_min, x_max = reduced_data[:, 0].min() - 0.1, reduced_data[:, 0].max() + 0.1
    y_min, y_max = reduced_data[:, 1].min() - 0.1, reduced_data[:, 1].max() + 0.1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

    '''
    print("xmin xmax", x_min, x_max)
    print("ymin ymax", y_min, y_max)
    print("xxmin xxmax", xx.min(), xx.max())
    print("yymin yymax", yy.min(), yy.max())
    '''

    # Obtain labels for each point in mesh. Use last trained model.
    Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    plt.figure(1)
    plt.clf()
    plt.imshow(Z, interpolation="nearest",
               extent=(xx.min(), xx.max(), yy.min(), yy.max()),
               cmap=plt.cm.Paired, aspect="auto", origin="lower")

    plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
    # Plot the centroids as a white X
    centroids = kmeans.cluster_centers_
    plt.scatter(centroids[:, 0], centroids[:, 1], marker="x", s=169, linewidths=3,
                color="pink", zorder=10)
    plt.title(f"K-means clustering on {method}-reduced features\n"
              "Centroids are marked with a cross")
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.xticks(())
    plt.yticks(())
    plt.savefig(f'{plot_dir}/2D-{method}.png', format='png')
    plt.show()
    mpl.rcParams.update(mpl.rcParamsDefault)
    plt.clf()


def check_multiple_types_per_case(df, type='beslissing'):
    '''
    Function to check whether we have the same amount of case rulings ('beslissing')
    as we have cases. Assumes 'ECLI' and 'type' column.
    '''

    # I used to have 'ECLI' as a column, but changed the load() function to have it as the dataframe index
    if 'ECLI' in df.keys():
        ECLIds = df['ECLI']
    else:
        # Otherwise, we assume the document identifiers to be the dataframe index
        ECLIds = df.index

    types = df.loc[df['type'] == type]

    if len(ECLIds.unique()) == len(types):
        print(f"Each of the {len(types)} cases has a single decision section")
    else:
        # If they do not match, return which cases have multiple decisions
        # It can happen a case has multiple 'beslissing' sections.
        # E.g. extra: "8 Beslissing omtrent in beslag genomen en niet teruggegeven geldbedrag" (ECLI:NL:RBNHO:2020:10314)
        print(f"The following cases have multiple sections of type {type}")

        if 'ECLI' in df.keys():
            df_type_per_ECLI = df.groupby('ECLI').apply(lambda x: len(x[x['type'] == type]))
        else:
            df_type_per_ECLI = df.groupby(df.index).apply(lambda x: len(x[x['type'] == type]))

        df_cases_with_multiple_types = df_type_per_ECLI[ df_type_per_ECLI > 1 ]
        print(df_cases_with_multiple_types)
        '''
        For 'beslissing':

        ECLI:NL:RBNHO:2020:10314    2
        ECLI:NL:RBNHO:2020:10959    2
        ECLI:NL:RBNHO:2020:11591    2

        For 'strafoplegging', we see that sometimes there is a
        'vordering' both from the 'officier from justitie' as
        well as from the 'benadeelde partij':

        ECLI:NL:RBAMS:2020:6643     2
        ECLI:NL:RBLIM:2020:10034    2
        ECLI:NL:RBLIM:2020:10342    2
        ECLI:NL:RBLIM:2020:10348    2
        ECLI:NL:RBLIM:2020:10349    2
        ECLI:NL:RBLIM:2020:9690     2
        ECLI:NL:RBLIM:2020:9691     2
        ECLI:NL:RBLIM:2020:9778     2
        ECLI:NL:RBLIM:2020:9853     2
        ECLI:NL:RBLIM:2020:9868     2
        ECLI:NL:RBLIM:2020:9942     2
        ECLI:NL:RBLIM:2020:9977     2
        ECLI:NL:RBLIM:2020:9978     2
        ECLI:NL:RBLIM:2020:9979     2
        ECLI:NL:RBLIM:2020:9980     2
        ECLI:NL:RBNHO:2020:10342    2
        ECLI:NL:RBNHO:2020:10368    2
        ECLI:NL:RBNNE:2020:4171     2
        ECLI:NL:RBNNE:2020:4172     2
        ECLI:NL:RBNNE:2020:4485     2
        ECLI:NL:RBROT:2020:12977    2
        ECLI:NL:RBROT:2020:12979    2
        '''


def cited_articles(df):
    '''
    Given a dataframe with a list of articles saved under the column 'articles',
    retrieve all cited (unique) law articles
    '''
    # Each lists is written to csv as a string, so evaluate them to lists of strings
    articles = df['articles'].apply(literal_eval)

    # Disregard empty lists
    articles = articles[articles.map(lambda x: len(x) > 0)]

    # Flatten
    articles = [ article for sub in articles for article in sub ]

    # Get unique values
    articles = sorted(np.unique(articles))

    '''
['04', '1', '10', '107', '10a', '11', '11b', '12', '13', '138', '14', '141', '14a', '14b', '14c', '14d', '14e', '14f', '14g', '15', '157', '163', '169', '175', '176', '177', '178', '179', '179a', '18', '184', '1990', '1994', '1a', '2', '2002', '2004', '2016', '2017', '2018', '21', '225', '228', '22b', '22c', '22d', '23', '231b', '239', '24', '240b', '242', '244', '245', '246', '247', '248', '248a', '248b', '249', '24c', '250', '254a', '26', '261', '266', '267', '27', '273f', '28', '282', '285', '285b', '287', '289', '29', '3', '300', '301', '302', '304', '307', '308', '31', '310', '311', '312', '317', '321', '326', '33', '336', '33a', '34', '350', '355', '36', '36b', '36c', '36d', '36e', '36f', '37a', '37b', '38', '38a', '38e', '38m', '38n', '38v', '38w', '38z', '3a', '4', '40', '416', '417b', '420', '420b', '420t', '45', '46', '47', '48', '49', '4b', '5', '51', '54', '55', '56', '57', '6', '60a', '61', '62', '63', '7', '72', '77a', '77c', '77g', '77i', '77m', '77n', '77s', '77w', '77x', '77y', '77z', '7a', '8', '853', '9', '91', '92', '9a']
    '''

    return articles

def check_articles(df):
    '''
    Article references are parsed from 'wettelijke voorschriften section'.
    This function performs some checks:

    - How many 'wettelijke voorschriften' sections are there? Does each case have one?
    - Which cases do not have a 'wettelijke voorschriften' section?
    - Print uniquely cited articles
    '''

    # I used to have 'ECLI' as a column, but changed the load() function to have it as the dataframe index
    if 'ECLI' in df.keys():
        ECLIds = df['ECLI']
    else:
        # Otherwise, we assume the document identifiers to be the dataframe index
        ECLIds = df.index

    # Unique cases
    print("Number of unique cases", len(ECLIds.unique()))

    # Sections with 'wettelijke voorschriften'
    voorschriften = df.loc[df['type'] == 'wettelijke voorschriften']
    print("Number of wettelijke voorschriften:", len(voorschriften))

    # Does each case have a wettelijke voorschriften section?
    if 'ECLI' in df.keys():
        df_voorschriften_per_ECLI = df.groupby('ECLI').apply(lambda x: len(x[x['type'] == 'wettelijke voorschriften']))
    else:
        df_voorschriften_per_ECLI = df.groupby(df.index).apply(lambda x: len(x[x['type'] == 'wettelijke voorschriften']))
    df_cases_without_voorschriften = df_voorschriften_per_ECLI[df_voorschriften_per_ECLI == 0]

    # Check wettelijke voorschriften sections where no articles are found
    print(len(df_cases_without_voorschriften), "cases without wettelijke voorschriften")
    print(df_cases_without_voorschriften)

    df_cases_with_multiple_voorschriften = df_voorschriften_per_ECLI[df_voorschriften_per_ECLI > 1]
    print(len(df_cases_with_multiple_voorschriften), "cases with multiple wettelijke voorschriften")
    print(df_cases_with_multiple_voorschriften)

    # Each lists is written to csv as a string, so evaluate them to lists of strings
    # articles = df['articles'].apply(literal_eval)
    # articles = articles[articles.map(lambda x: len(x) > 0)]

    # Print all unique cited articles
    print("Unique cited articles")
    print(cited_articles(df))


def construct_mask(types: (list, np.array), types_keep: (list, np.array)):
    '''
    Convenience function to construct a logical mask

    types:          A flat list or array of input types
    types_keep:     A flat list or array of types to keep
    '''
    if isinstance(types, list) or isinstance(types, pd.Series):
        types = np.array(types)
    if isinstance(types_keep, list):
        types_keep = np.array(types_keep)

    # Construct a logical filter on the section types
    if types_keep is not None:
        if len(types_keep) > 1:
            mask = np.logical_or(types == types_keep[0], types == types_keep[1])
            for type in types_keep[2:]:
                mask = np.logical_or(types == type, mask)
        elif len(types_keep) == 1:
            mask = np.nonzero(types == types_keep[0])
        else:
            # If empty list, do not filter on sections
            mask = np.nonzero(types)
    else:
        # If None, do not filter on sections
        mask = np.nonzero(types)
    return mask


def kmeans_elbow_curve(X, style=2, max=15, metric='distortion'):
    '''
    Curve to help automatically define a good amount of clusters
    for k-means, based on the inertia score. Does not use the
    custom Clusterer but only K-Means.

    style:      if 1, use plain elbow method using sklearn; if 2, use nice visualization from the Yellowbrick library
    max:        maximum number of clusters to try
    metric:     uses 'distortion' by default (sum of squared distances from each point to its assigned cluster center)
                another possible value is 'silhouette' or 'calinski_harabasz'

    '''

    elbow_value = 0  # The elbow value is the point where a curve starts to flatten out
    Ks = (2, max)  # K clusters to try

    if style == 1:
        # Computation 'by hand'
        Cs = range(*Ks)
        if metric.lower() == 'silhouette':
            scores = [silhouette_score(X, KMeans(n_clusters=c).fit(X).labels_) for c in Cs]
        elif metric.lower() == 'calinski_harabasz':
            scores = [calinski_harabasz_score(X, KMeans(n_clusters=c).fit(X).labels_) for c in Cs]
        if metric.lower() == 'distortion':
            scores = [KMeans(n_clusters=c).fit(X).inertia_ for c in Cs]
        plt.plot(Cs, scores)
        plt.show()
        # TODO We have not yet automatically determined the elbow value
        print("WARNING: Automatic determination of elbow value not yet determined for style=1!")
    else:
        # Very nice yellowbrick visualization
        visualizer = KElbowVisualizer(
                KMeans(), k=Ks,
                metric=metric)
        visualizer.fit(X)
        visualizer.show()
        elbow_value = visualizer.elbow_value_

    return elbow_value


def silhouette_plot(X, cluster_labels):
    '''
    Example: https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html#sphx-glr-auto-examples-cluster-plot-kmeans-silhouette-analysis-py
    '''

    n_clusters = len(np.unique(cluster_labels))

    sample_silhouette_values = silhouette_samples(X, cluster_labels)
    silhouette_avg = silhouette_score(X, cluster_labels)

    fig, ax1 = plt.subplots(1, 1)
    fig.set_size_inches(18, 7)

    # Silhouette is between -1 and 1
    # It won't be super negative, so we can limit the negative range a bit
    ax1.set_xlim([-0.4, 1])
    # The (n_clusters+1)*10 is for inserting blank space between silhouette
    # plots of individual clusters, to demarcate them clearly.
    ax1.set_ylim([0, len(X) + (n_clusters + 1) * 10])
    ax1.set_yticks([])  # Clear the yaxis labels / ticks
    ax1.set_xticks([-0.2, 0, 0.2, 0.4, 0.6, 0.8, 1])
    ax1.set_title("Silhouette plot for individual clusters.")
    ax1.set_xlabel("Silhouette coefficient values")
    ax1.set_ylabel("Cluster label")

    # The vertical line for average silhouette score of all the values
    ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

    y_lower = 10
    for i in range(n_clusters):
        ith_cluster_scores = sample_silhouette_values[cluster_labels == i]
        ith_cluster_scores.sort()
        ith_cluster_size = ith_cluster_scores.shape[0]
        y_upper = y_lower + ith_cluster_size

        # color = cm.nipy_spectral(float(i) / n_clusters)
        cmap = cm.get_cmap('tab20')
        color = cmap(i)

        ax1.fill_betweenx(
            np.arange(y_lower, y_upper),
            0,
            ith_cluster_scores,
            facecolor=color,
            edgecolor=color,
            alpha=0.7,
        )

        # Label with cluster numbers
        ax1.text(-0.05, y_lower + 0.5 * ith_cluster_size, str(i))

        # Compute the new y_lower for next plot so they don't overlap
        y_lower = y_upper + 10  # 10 for the 0 samples

    plt.show()


def split_dataset_on_date(df, date):
    '''
    Splits a data set in two sets based on a date.
    Date are YYYY-MM-DD
    Example:

    Begin: 2021/01/01
    End: 2021/12/31

    To split halfway on year, provide for `date`
    '2021/07/01', '2021-07-01', as pd.TimeStamp
    or datetime.datetime, or np.datetime64.
    '''
    # Set 'date' strings as datetime objects so pandas can sort on it
    df['date'] = pd.to_datetime(df['date'])
    mask_before = df['date'] < date
    # assuming we split by the first of the month,
    # >= keeps days from the same month in the same set
    mask_after = df['date'] >= date
    before = df.loc[mask_before]
    after = df.loc[mask_after]
    return before, after


def convert_vectors_to_binary(vectors):
    '''
    Straf vectors produced by strafmaat.py also store
    the height of the punishment. This function instead
    converts this to binary vectors. Vectors are stored
    as tuples, not as array. However, to do this easily
    we'll convert to numpy array as an intermediate step.

    vectors:
        list or array-like with vectors stored as tuples

    returns:
        array with the vector values converted to {0, 1}
    '''

    vectors = np.array(vectors)
    binary_vectors = (vectors > 0).astype(int)
    return binary_vectors


def diff_pattern(pattern_from: str, pattern_to: str):
    '''
    Utility function that shows how to change one pattern into another
    Useful for comparing two regular expressions.
    '''
    print('{}\n=>\n{}'.format(pattern_from, pattern_to))
    for i, s in enumerate(difflib.ndiff(pattern_from, pattern_to)):
        if s[0] == ' ':
            continue
        elif s[0] == '-':
            print(u'Delete "{}" from position {}'.format(s[-1], i))
        elif s[0] == '+':
            print(u'Add "{}" to position {}'.format(s[-1], i))
