package show_menu;

use CGI qw(:standard escapeHTML); 

use utf8; 

use strict;

require './Modules/Common.pm'; 
require './Modules/DB.pm';

sub run {
  my $chosen_kap = $Common::cgi->param('kapitel') // '';
  my $chosen_thm = $Common::cgi->param('thema')   // '';
  my $rows_kap = 
    $DB::dbh->selectall_arrayref( 
      q{ select kap_kürzel, kapitel, count(th_kürzel) from 
        (select kap_kürzel, kapitel, th_kürzel, count(frage_id) as cnt from kapitel_themen_fragen group by kap_kürzel,th_kürzel,kapitel) where cnt>0 group by kap_kürzel, kapitel;
      } 
    );

  my @kap_values = (''); my %kap_labels = ('' => ' -- wähle die Kapitel -- ');
  for my $r (@$rows_kap) {
    my ($code, $name, $cnt) = @$r;
    next unless defined $code;
    $name = '' unless defined $name;
    push @kap_values, $code;
    $kap_labels{$code} = "$name ($cnt Themen)"; # "$name ($code)";
  }
  my $n_suggest = $Common::DEFAULT_N; my @thm_values; my %thm_labels;
  if ($chosen_kap ne '') {
    my $rows_thm = 
      $DB::dbh->selectall_arrayref( 
          q{ select th_kürzel, thema, cnt from (select kap_kürzel, th_kürzel,thema,count(frage_id) as cnt from kapitel_themen_fragen group by kap_kürzel,th_kürzel,thema) 
            where cnt>0 and kap_kürzel=? }, undef, $chosen_kap );
    if ($rows_thm && @$rows_thm) {
      @thm_values = (''); #my $r = pop @$rows_thm; $n_suggest= $$r[2]; $chosen_thm=$$r[0];
      %thm_labels = ( '' =>  ' -- Wähle das Thema -- '); # "$$r[1] ($chosen_thm: $n_suggest Fragen)" ); # 
      for my $r (@$rows_thm) {
        my ($code, $name,$cnt) = @$r;
        next unless defined $code;
        $name = '' unless defined $name;
        push @thm_values, $code;
        $thm_labels{$code} = "$name ($cnt Fragen)"; #"$name ($code)";
      }
    }
  }
  
  HTML::page_header("Quiz – menu");

  Common::debug_block();
  
  my $method='GET';
  # print h2("Kapitels und Themawahl [$chosen_kap, $chosen_thm]");

  print qq{
    <style>
      .pagebox{ width: 100%; max-width: 95vw; position: static; margin-top: 0px; }
      html, body { height: 100%; margin: 0; }
      body { min-height: 100vh; display: inline-box; align-items: center; justify-content: center; padding: 10%; box-sizing: border-box; }
    </style>  
  };

  my $ua = $ENV{'HTTP_USER_AGENT'} // '';
  print "<div class='pagebox'>";
  print "<div style='color: gray; font-size: 0.5em;'>$ua [<script>document.write(window.innerWidth+'x'+window.innerHeight)</script>]</div>";
  print h2("Kapitels und Themawahl");
  print start_form(-method=>'$method', -action=>$Common::SELF, -class=>'row');
  print hidden(-name=>'action', -value=>'menu');
  print "Kapitel: ", popup_menu( -name=>'kapitel', -values   => \@kap_values, -labels   => \%kap_labels, -default  => $chosen_kap, -onchange => 'this.form.submit()' );
  print end_form;
  print qq{<div class="sep"></div>};

  if ($chosen_kap ne '' && @thm_values) {
    print start_form(-method=>'$method', -action=>$Common::SELF, -class=>'row');
    # print hidden(-name=>'debug', -value=>1) if $Common::cgi->param('debug');
    print hidden(-name=>'kapitel', -value=>$chosen_kap);
    print "Thema: ", 
      popup_menu( 
        -id => 'thema',
        -name=>'thema', -values  => \@thm_values, -labels   => \%thm_labels, -default  => $chosen_thm, 
        -onchange => 'this.form.submit();' ### 
        # -onchange => '',
      ), br();
    print qq{<div class="sep"></div>};

    my $cnt = 0; my $n_suggest = '';
    if ($chosen_kap ne '' && $chosen_thm ne '') {
      ($cnt) = $DB::dbh->selectrow_array(  q{SELECT count(*) FROM fragen WHERE "kap_kürzel" = ? AND "th_kürzel" = ?}, undef, $chosen_kap, $chosen_thm );
      $cnt ||= 0;
      $n_suggest = $cnt if $cnt > 0;
    }

    if (($Common::cgi->param('err') // '') eq 'invalid_n' && $cnt > 0) {
      print p({class=>'warn'}, "Bitte eine gültige Anzahl der Fragen angeben (1 bis $cnt).");
    }

    my $disabled = ($chosen_kap ne '' && $chosen_thm ne '') ? '' : 'disabled';

    my $n_attrs = $cnt > 0 ? qq{min="1" max="$cnt"} : q{min="1"};
    print qq{Anzahl der Fragen: <input type="number" name="n" $n_attrs step="1" value="$n_suggest" size="3" $disabled>}, br();

    print qq{ <button class="btn" type="submit" name="action" value="start" id="test-start" style="margin: 2vh auto auto 25vw; padding: 15px 30px 15px 30px;" $disabled>Start</button> };

    # print qq{$n_suggest zu nehmenden Fragen};

    # my $dbg = $Common::cgi->param('debug') ? "&debug=1" : "";   
    # print "&nbsp;&nbsp;&nbsp;", a({href=>"$Common::SELF?action=reset$dbg", class=>'small' }, "Sessionneustart");
    print end_form;
    print "</div>";

  } elsif ($chosen_kap ne '') {
    print p({class=>'warn'}, "Keine Themen in dieser Kapitel.");
  } else {
    #print p({class=>'small'}, "Bitte die Kapitel wählen.");
  } # ($chosen_kap ne '' && @thm_values)

  HTML::page_footer();
  exit;
} # show_menu - Ende
