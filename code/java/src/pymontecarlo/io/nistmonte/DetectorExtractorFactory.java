package pymontecarlo.io.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.jdom.Element;

import pymontecarlo.input.nistmonte.AngularDetectorFactory;
import pymontecarlo.input.nistmonte.Detector;
import pymontecarlo.input.nistmonte.ElectronFractionDetector;
import pymontecarlo.input.nistmonte.EnergyDetectorFactory;
import pymontecarlo.input.nistmonte.PhotonIntensityDetector;
import pymontecarlo.input.nistmonte.PhotonSpectrumDetector;
import pymontecarlo.input.nistmonte.TimeDetector;

/**
 * Factory of detector extractors.
 * 
 * @author ppinard
 */
public class DetectorExtractorFactory implements
        ExtractorFactory<DetectorExtractor> {

    /** Photon intensity detector extractor. */
    public static final DetectorExtractor PHOTON_INTENSITY =
            new AbstractDetectorExtractor(
                    "pymontecarlo.input.base.detector.PhotonIntensityDetector") {

                @Override
                public Detector extract(Element detectorElement)
                        throws IOException, EPQException {
                    double takeOffAngle = extractTakeOffAngle(detectorElement);
                    double azimuthAngle = extractAzimuthAngle(detectorElement);

                    return new PhotonIntensityDetector(takeOffAngle,
                            azimuthAngle);
                }
            };

    /** Backscattered electron energy detector extractor. */
    public static final DetectorExtractor BACKSCATTERED_ELECTRON_ENERGY =
            new AbstractDetectorExtractor(
                    "pymontecarlo.input.base.detector.BackscatteredElectronEnergyDetector") {

                @Override
                public Detector extract(Element detectorElement)
                        throws IOException, EPQException {
                    double min = extractLowerLimit(detectorElement);
                    double max = extractUpperLimit(detectorElement);
                    int channels = extractChannels(detectorElement);
                    return EnergyDetectorFactory.createBackscatteredElectron(
                            min, max, channels);
                }
            };

    /** Transmitted electron energy detector extractor. */
    public static final DetectorExtractor TRANSMITTED_ELECTRON_ENERGY =
            new AbstractDetectorExtractor(
                    "pymontecarlo.input.base.detector.TransmittedElectronEnergyDetector") {

                @Override
                public Detector extract(Element detectorElement)
                        throws IOException, EPQException {
                    double min = extractLowerLimit(detectorElement);
                    double max = extractUpperLimit(detectorElement);
                    int channels = extractChannels(detectorElement);
                    return EnergyDetectorFactory.createTransmittedElectron(min,
                            max, channels);
                }
            };

    /** Backscattered electron elevation angular detector extractor. */
    public static final DetectorExtractor BACKSCATTERED_ELECTRON_ELEVATION_ANGULAR =
            new AbstractDetectorExtractor(
                    "pymontecarlo.input.base.detector.BackscatteredElectronPolarAngularDetector") {

                @Override
                public Detector extract(Element detectorElement)
                        throws IOException, EPQException {
                    double min = extractLowerLimit(detectorElement);
                    double max = extractUpperLimit(detectorElement);
                    int channels = extractChannels(detectorElement);
                    return AngularDetectorFactory
                            .createBackscatteredElevationAngular(min, max,
                                    channels);
                }
            };

    /** Transmitted electron elevation angular detector extractor. */
    public static final DetectorExtractor TRANSMITTED_ELECTRON_ELEVATION_ANGULAR =
            new AbstractDetectorExtractor(
                    "pymontecarlo.input.base.detector.TransmittedElectronPolarAngularDetector") {

                @Override
                public Detector extract(Element detectorElement)
                        throws IOException, EPQException {
                    double min = extractLowerLimit(detectorElement);
                    double max = extractUpperLimit(detectorElement);
                    int channels = extractChannels(detectorElement);
                    return AngularDetectorFactory
                            .createTransmittedElevationAngular(min, max,
                                    channels);
                }
            };

    /** Backscattered electron azimuthal angular detector extractor. */
    public static final DetectorExtractor BACKSCATTERED_ELECTRON_AZIMUTHAL_ANGULAR =
            new AbstractDetectorExtractor(
                    "pymontecarlo.input.base.detector.BackscatteredElectronAzimuthalAngularDetector") {

                @Override
                public Detector extract(Element detectorElement)
                        throws IOException, EPQException {
                    double min = extractLowerLimit(detectorElement);
                    double max = extractUpperLimit(detectorElement);
                    int channels = extractChannels(detectorElement);
                    return AngularDetectorFactory
                            .createBackscatteredAzimuthalAngular(min, max,
                                    channels);
                }
            };

    /** Transmitted electron azimuthal angular detector extractor. */
    public static final DetectorExtractor TRANSMITTED_ELECTRON_AZIMUTHAL_ANGULAR =
            new AbstractDetectorExtractor(
                    "pymontecarlo.input.base.detector.TransmittedElectronAzimuthalAngularDetector") {

                @Override
                public Detector extract(Element detectorElement)
                        throws IOException, EPQException {
                    double min = extractLowerLimit(detectorElement);
                    double max = extractUpperLimit(detectorElement);
                    int channels = extractChannels(detectorElement);
                    return AngularDetectorFactory
                            .createTransmittedAzimuthalAngular(min, max,
                                    channels);
                }
            };

    /** Photon spectrum detector extractor. */
    public static final DetectorExtractor PHOTON_SPECTRUM =
            new AbstractDetectorExtractor(
                    "pymontecarlo.input.base.detector.PhotonSpectrumDetector") {

                @Override
                public Detector extract(Element detectorElement)
                        throws IOException, EPQException {
                    double min = extractLowerLimit(detectorElement);
                    double max = extractUpperLimit(detectorElement);
                    int channels = extractChannels(detectorElement);

                    double takeOffAngle = extractTakeOffAngle(detectorElement);
                    double azimuthAngle = extractAzimuthAngle(detectorElement);

                    return new PhotonSpectrumDetector(takeOffAngle,
                            azimuthAngle, min, max, channels);
                }
            };

    /** Time detector extractor. */
    public static final DetectorExtractor TIME = new AbstractDetectorExtractor(
            "pymontecarlo.input.base.detector.TimeDetector") {

        @Override
        public Detector extract(Element detectorElement) throws IOException,
                EPQException {
            return new TimeDetector();
        }
    };

    /** Electron fraction detector extractor. */
    public static final DetectorExtractor ELECTRON_FRACTION =
            new AbstractDetectorExtractor(
                    "pymontecarlo.input.base.detector.ElectronFractionDetector") {

                @Override
                public Detector extract(Element detectorElement)
                        throws IOException, EPQException {
                    return new ElectronFractionDetector();
                }
            };



    @Override
    public List<DetectorExtractor> getAllExtractors() {
        List<DetectorExtractor> extractors = new ArrayList<DetectorExtractor>();

        extractors.add(PHOTON_INTENSITY);
        extractors.add(BACKSCATTERED_ELECTRON_ENERGY);
        extractors.add(TRANSMITTED_ELECTRON_ENERGY);
        extractors.add(BACKSCATTERED_ELECTRON_ELEVATION_ANGULAR);
        extractors.add(TRANSMITTED_ELECTRON_ELEVATION_ANGULAR);
        extractors.add(BACKSCATTERED_ELECTRON_AZIMUTHAL_ANGULAR);
        extractors.add(TRANSMITTED_ELECTRON_AZIMUTHAL_ANGULAR);
        extractors.add(PHOTON_SPECTRUM);
        extractors.add(TIME);
        extractors.add(ELECTRON_FRACTION);

        return Collections.unmodifiableList(extractors);
    }

}
