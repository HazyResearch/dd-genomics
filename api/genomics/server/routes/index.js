var express = require('express');
var router = express.Router();
var path = require('path');
var pg = require('pg');
var connectionString = process.env.DATABASE_URL || 'postgres://ajratner@localhost:6432/genomics_ajratner';

/* GET G-P relations by gene id (ensembl) */
router.get('/api/gp/:gene_id', function(req, res) {
  var results = [];
  var geneId = req.params.gene_id;
  console.log("GET request for geneId=" + geneId);

  // Get a Postgres client from the connection pool
  pg.connect(connectionString, function(err, client, done) {

    // NOTE: support either e.g. "ENSG00000101255" or "ENSG00000101255:TRIB3" formats
    var limit = 5;

    // TODO: figure out how to handle association / causation
    var query = client.query("SELECT gp.relation_id, gp.doc_id, gp.gene_entity, gp.gene_wordidxs, gp.pheno_entity, gp.pheno_wordidxs, gp.expectation, s.words FROM genepheno_relations_is_correct_inference gp, sentences s WHERE gp.doc_id = s.doc_id AND gp.sent_id = s.sent_id AND gp.gene_entity LIKE ($1) ORDER BY expectation DESC LIMIT ($2);", [geneId+"%", limit]);

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
