SELECT oc.citing, oc.cited
FROM open_citations oc
JOIN cr_publications citing_cp ON citing_cp.doi = oc.citing
JOIN cr_publications cited_cp ON cited_cp.doi = oc.cited;