var express = require('express');
var router = express.Router();
var path = require('path');
var pg = require('pg');
var connectionString = 'postgres://ajratner@localhost:6432/genomics_production';

/* GET G-P relations by gene id (ensembl) */
router.get('/api/gp/', function(req, res) {
  var results = [];
  var geneId = req.query.geneId;
  var expC = parseFloat(req.query.expC);
  expC = (expC > 0) ? Math.min(1.0, expC) : 0.0;
  var expA = parseFloat(req.query.expA);
  expA = (expA > 0) ? Math.min(1.0, expA) : 0.0;
  var maxResults = parseInt(req.query.maxResults);
  maxResults = (maxResults > 0) ? maxResults : 10;
  var page = parseInt(req.query.page);
  page = (page > 0) ? page : 0;
  console.log("GET request for geneId='" + geneId + "%' where E[C] >= " + expC + " AND E[A] >= " + expA + " (page:" + page + " maxResults:" + maxResults + ")");

  // Get a Postgres client from the connection pool
  pg.connect(connectionString, function(err, client, done) {

    // NOTE: support either e.g. "ENSG00000101255" or "ENSG00000101255:TRIB3" formats
    // NOTE: We pre-compute the aggregation at entity level but only for E > 0.5
    var sql = 'SELECT gene_entity, pheno_entity, relation_ids, doc_ids, sent_ids, gene_wordidxs, pheno_wordidxs, words, a_expectations, c_expectations FROM genepheno_entity_level WHERE gene_entity LIKE ($1) AND ((($2) > 0.0 AND max_a_expectation >= ($2)) OR (($3) > 0.0 AND max_c_expectation >= ($3))) LIMIT ($4) OFFSET ($5);'
    var query = client.query(sql, [geneId+'%', expA, expC, maxResults, maxResults*page]);

    // Stream results back one row at a time
    query.on('row', function(row) {
      results.push(row);
    });

    // After all data is returned, close connection and return results
    query.on('end', function() {
      client.end();
      return res.json(results);
    });

    // Handle Errors
    if(err) {
      console.log(err);
    }
  });
});

/* GET home page- API demo. */
router.get('/', function(req, res, next) {
  res.sendFile(path.join(__dirname, '../', '../', 'client', 'views', 'index.html'));
  //res.render('index', { title: 'Genomics API' });
});

module.exports = router;
