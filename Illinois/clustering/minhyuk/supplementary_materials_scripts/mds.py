from sklearn.manifold import MDS

dist_mat = None
# dist_mat should be a 2d array that serves as input to the MDS algorithm
if (not distmat):
    raise Exception("Distance matrix required")

mds = MDS(dissimilarity="precomputed", random_state=0)
dist_mat_transform = mds.fit_transform(dist_mat)

# dist_mat_transform[:,0] contains the x-coordinates of the new points
# dist_mat_transform[:,1] contains the y-coordinates of the new points
