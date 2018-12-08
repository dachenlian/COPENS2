use Test::More tests => 34;
## run some tests on (very small) UTF-8 encoded corpus

use utf8;
use strict;
use warnings;

use Encode;
use CWB::CL;

$CWB::CL::Registry = "data/registry"; # use local copy of HOLMES-DE corpus

our $C = new CWB::CL::Corpus "HOLMES-DE";      # -- access corpus and word attribute
isa_ok($C, "CWB::CL::Corpus", "corpus object for HOLMES-DE corpus") # T1
  or BAIL_OUT("failed to access corpus HOLMES-DE");

our $Word = $C->attribute("word", "p");
isa_ok($Word, "CWB::CL::PosAttrib", "attribute object for HOLMES-DE.word") # T2
  or BAIL_OUT("failed to access attribute HOLMES-DE.word");

our $n_types = $Word->max_id;
diag("HOLMES-DE contains $n_types distinct word forms");

our @wordlist = map {decode("utf8", $_)} $Word->id2str(0 .. $n_types-1);

## validate PCRE regexp in CWB against same regexp in Perl
## (each function call executes 2 tests, with and without cl_optimize)
sub validate_regexp {
  my $regexp = shift;
  my $casefold = shift || "";
  my $perl_flags = ($casefold) ? "(?i)" : "";
  my $cwb_flags = ($casefold) ? "c" : "";

  my $perl_regexp = qr/^${perl_flags}(?:${regexp})$/;
  our @perl_id = grep { $wordlist[$_] =~ $perl_regexp } 0 .. $#wordlist;
  # -- enable diag() in order to identify discrepancies
  # diag("PERL:    ", join(" ", map {encode("utf8", $_)} @wordlist[@perl_id]), "\n");
  
  foreach my $optimize (0, 1) {
    CWB::CL::set_optimize($optimize);
    my $opt_status = $optimize ? "+opt:" : ":    ";
    my @cwb_id = $Word->regex2id(encode("utf8", $regexp), $cwb_flags);
    # -- enable diag() in order to identify discrepancies
    # diag("CWB$opt_status ", join(" ", $Word->id2str(@cwb_id)), "\n");
    is_deeply(\@cwb_id, \@perl_id, "validate regexp /$regexp/ $casefold".$opt_status);
  }
  CWB::CL::set_optimize(0);
  
  
}

validate_regexp('[a-z]+'); # T3 (each of the following lines runs two tests)
validate_regexp('\PL+');
validate_regexp('\p{Lu}\p{Ll}+');
validate_regexp('.*[aeiouäöü]{2}.*');
validate_regexp('.*(\pL).*\1.*\1.*');

## test case-insensitive matching (which was broken after switching to PCRE in CWB v3.4.x)
validate_regexp('[a-z]+', '%c'); # T13
validate_regexp('[A-Z]+', '%c'); 
validate_regexp('[a-z]+che[nr]', '%c');
validate_regexp('\pL+', '%c'); # CWB's old case-folding would turn \pL into \pl (syntax error)
validate_regexp('\PL+', '%c'); 
validate_regexp('sa.', '%c');  # CWB's old case-folding turned German ß into ss, so /sa./ doesn't match "saß"
validate_regexp('sa..', '%c'); # this shouldn't match anything
validate_regexp('da.', '%c');  # should match "das" and "daß" (not in corpus), but not "dass"
validate_regexp('(?!dass)daß', '%c');  # Perl identifies ß and ss in case-insensitive mode, but PCRE doesn't
validate_regexp('(?!dass)daß?', '%c'); # CWB used to match "dass" and "das" instead of "da"

validate_regexp('z\w+'); # T33: make sure that \w is set up to use Unicode props in PCRE






