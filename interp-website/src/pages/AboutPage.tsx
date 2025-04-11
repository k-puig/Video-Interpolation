function AboutPage() {
  return (
    <div className="container">
      <h1>About This Site</h1>
      <p>
        This website allows you to upload videos of any type, and in turn receive a neural
        network-interpolated video. By processing your video with our custom neural network, the
        number of frames in the video is nearly doubled (to be exact, 2n-1 total frames in the new
        video).
      </p>
      <p>
        For more information generally on what video interpolation is, check
        out <a href="https://en.wikipedia.org/wiki/Motion_interpolation">this Wikipedia article.</a>
      </p>
    </div>
  );
}

export default AboutPage;