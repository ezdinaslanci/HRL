function [] = betterPlot()

  cm0 = load('cm0-2.txt');
  
  fig = figure;
  plot(cm0(:,[2,5,1,6,7]), 'linewidth', 4);

  leg = legend('P(→|↓)', 'P(↓|→)', 'P(↓|↓)', 'P(→|→)', 'P(↑|→)');
  set(leg, 'FontSize', 16);

  set(gca, 'xtick', [240, 480]);
  set(gca, 'fontsize', 16);

  title('First Order Markov Dependencies');
  xlabel('Action Sequence');
  ylabel('Probability');

  grid on;

end 