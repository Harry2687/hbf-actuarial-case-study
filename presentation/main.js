import './style.css';
import Reveal from 'reveal.js';

// Initialize Reveal.js
const deck = new Reveal();
deck.initialize({
  hash: true,
  transition: 'slide', // none/fade/slide/convex/concave/zoom
  backgroundTransition: 'fade',
  controls: true,
  progress: true,
  center: true,
  autoAnimate: true,
  width: 1024,
  height: 768,
  margin: 0.04,
  minScale: 0.2,
  maxScale: 2.0
});
