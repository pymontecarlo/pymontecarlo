package pymontecarlo.io.nistmonte;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import gov.nist.microanalysis.EPQLibrary.EPQException;

import java.io.IOException;

import org.jdom.Element;
import org.junit.Test;

import pymontecarlo.input.nistmonte.ChannelDetector;
import pymontecarlo.input.nistmonte.Detector;
import pymontecarlo.input.nistmonte.PhotonDetector;

public class DetectorExtractorFactoryTest {

    public static Element createPhotonIntensityDetectorElement(String key) {
        Element element =
                new Element(
                        "pymontecarlo.input.base.detector.PhotonIntensityDetector");
        element.setAttribute("_key", key);

        element.setAttribute("elevation_min",
                Double.toString(Math.toRadians(30)));
        element.setAttribute("elevation_max",
                Double.toString(Math.toRadians(50)));
        element.setAttribute("azimuth_min", Double.toString(Math.toRadians(0)));
        element.setAttribute("azimuth_max",
                Double.toString(Math.toRadians(180)));

        return element;
    }



    @Test
    public void testPHOTON_INTENSITY() throws IOException, EPQException {
        Element element = createPhotonIntensityDetectorElement("det1");

        DetectorExtractor extractor = DetectorExtractorFactory.PHOTON_INTENSITY;
        assertTrue(extractor.canExtract(element));

        PhotonDetector det = (PhotonDetector) extractor.extract(element);
        assertEquals(Math.toRadians(40.0), det.getTakeOffAngle(), 1e-4);
        assertEquals(Math.toRadians(90.0), det.getAzimuthAngle(), 1e-4);
    }



    public static Element createBackscatteredElectronEnergyDetectorElement(
            String key) {
        Element element =
                new Element(
                        "pymontecarlo.input.base.detector.BackscatteredElectronEnergyDetector");
        element.setAttribute("_key", key);

        element.setAttribute("limit_min", "0.0");
        element.setAttribute("limit_max", "5.0");
        element.setAttribute("channels", "100");

        return element;
    }



    @Test
    public void testBACKSCATTERED_ELECTRON_ENERGY() throws IOException,
            EPQException {
        Element element =
                createBackscatteredElectronEnergyDetectorElement("det1");

        DetectorExtractor extractor =
                DetectorExtractorFactory.BACKSCATTERED_ELECTRON_ENERGY;
        assertTrue(extractor.canExtract(element));

        ChannelDetector det = (ChannelDetector) extractor.extract(element);
        assertEquals(0.0, det.getMinimumLimit(), 1e-4);
        assertEquals(5.0, det.getMaximumLimit(), 1e-4);
        assertEquals(100, det.getChannels());
        assertEquals(0.05, det.getChannelWidth(), 1e-4);
    }



    public static Element createTransmittedElectronEnergyDetector(String key) {
        Element element =
                new Element(
                        "pymontecarlo.input.base.detector.TransmittedElectronEnergyDetector");
        element.setAttribute("_key", key);

        element.setAttribute("limit_min", "0.0");
        element.setAttribute("limit_max", "5.0");
        element.setAttribute("channels", "100");

        return element;
    }



    @Test
    public void testTRANSMITTED_ELECTRON_ENERGY() throws IOException,
            EPQException {
        Element element = createTransmittedElectronEnergyDetector("det1");

        DetectorExtractor extractor =
                DetectorExtractorFactory.TRANSMITTED_ELECTRON_ENERGY;
        assertTrue(extractor.canExtract(element));

        ChannelDetector det = (ChannelDetector) extractor.extract(element);
        assertEquals(0.0, det.getMinimumLimit(), 1e-4);
        assertEquals(5.0, det.getMaximumLimit(), 1e-4);
        assertEquals(100, det.getChannels());
        assertEquals(0.05, det.getChannelWidth(), 1e-4);
    }



    public static Element createBackscatteredElectronPolarAngularDetector(
            String key) {
        Element element =
                new Element(
                        "pymontecarlo.input.base.detector.BackscatteredElectronPolarAngularDetector");
        element.setAttribute("_key", key);

        element.setAttribute("limit_min", "0.0");
        element.setAttribute("limit_max", "5.0");
        element.setAttribute("channels", "100");

        return element;
    }



    @Test
    public void testBACKSCATTERED_ELECTRON_ELEVATION_ANGULAR()
            throws IOException, EPQException {
        Element element =
                createBackscatteredElectronPolarAngularDetector("det1");

        DetectorExtractor extractor =
                DetectorExtractorFactory.BACKSCATTERED_ELECTRON_ELEVATION_ANGULAR;
        assertTrue(extractor.canExtract(element));

        ChannelDetector det = (ChannelDetector) extractor.extract(element);
        assertEquals(0.0, det.getMinimumLimit(), 1e-4);
        assertEquals(5.0, det.getMaximumLimit(), 1e-4);
        assertEquals(100, det.getChannels());
        assertEquals(0.05, det.getChannelWidth(), 1e-4);
    }



    public static Element createTransmittedElectronPolarAngularDetector(
            String key) {
        Element element =
                new Element(
                        "pymontecarlo.input.base.detector.TransmittedElectronPolarAngularDetector");
        element.setAttribute("_key", key);

        element.setAttribute("limit_min", "0.0");
        element.setAttribute("limit_max", "5.0");
        element.setAttribute("channels", "100");

        return element;
    }



    @Test
    public void testTRANSMITTED_ELECTRON_ELEVATION_ANGULAR()
            throws IOException, EPQException {
        Element element = createTransmittedElectronPolarAngularDetector("det1");

        DetectorExtractor extractor =
                DetectorExtractorFactory.TRANSMITTED_ELECTRON_ELEVATION_ANGULAR;
        assertTrue(extractor.canExtract(element));

        ChannelDetector det = (ChannelDetector) extractor.extract(element);
        assertEquals(0.0, det.getMinimumLimit(), 1e-4);
        assertEquals(5.0, det.getMaximumLimit(), 1e-4);
        assertEquals(100, det.getChannels());
        assertEquals(0.05, det.getChannelWidth(), 1e-4);
    }



    public static Element createBackscatteredElectronAzimuthalAngularDetector(
            String key) {
        Element element =
                new Element(
                        "pymontecarlo.input.base.detector.BackscatteredElectronAzimuthalAngularDetector");
        element.setAttribute("_key", key);

        element.setAttribute("limit_min", "0.0");
        element.setAttribute("limit_max", "5.0");
        element.setAttribute("channels", "100");

        return element;
    }



    @Test
    public void testBACKSCATTERED_ELECTRON_AZIMUTHAL_ANGULAR()
            throws IOException, EPQException {
        Element element =
                createBackscatteredElectronAzimuthalAngularDetector("det1");

        DetectorExtractor extractor =
                DetectorExtractorFactory.BACKSCATTERED_ELECTRON_AZIMUTHAL_ANGULAR;
        assertTrue(extractor.canExtract(element));

        ChannelDetector det = (ChannelDetector) extractor.extract(element);
        assertEquals(0.0, det.getMinimumLimit(), 1e-4);
        assertEquals(5.0, det.getMaximumLimit(), 1e-4);
        assertEquals(100, det.getChannels());
        assertEquals(0.05, det.getChannelWidth(), 1e-4);
    }



    public static Element createTransmittedElectronAzimuthalAngularDetector(
            String key) {
        Element element =
                new Element(
                        "pymontecarlo.input.base.detector.TransmittedElectronAzimuthalAngularDetector");
        element.setAttribute("_key", key);

        element.setAttribute("limit_min", "0.0");
        element.setAttribute("limit_max", "5.0");
        element.setAttribute("channels", "100");

        return element;
    }



    @Test
    public void testTRANSMITTED_ELECTRON_AZIMUTHAL_ANGULAR()
            throws IOException, EPQException {
        Element element =
                createTransmittedElectronAzimuthalAngularDetector("det1");

        DetectorExtractor extractor =
                DetectorExtractorFactory.TRANSMITTED_ELECTRON_AZIMUTHAL_ANGULAR;
        assertTrue(extractor.canExtract(element));

        ChannelDetector det = (ChannelDetector) extractor.extract(element);
        assertEquals(0.0, det.getMinimumLimit(), 1e-4);
        assertEquals(5.0, det.getMaximumLimit(), 1e-4);
        assertEquals(100, det.getChannels());
        assertEquals(0.05, det.getChannelWidth(), 1e-4);
    }



    public static Element createPhotonSpectrumDetector(String key) {
        Element element =
                new Element(
                        "pymontecarlo.input.base.detector.PhotonSpectrumDetector");
        element.setAttribute("_key", key);

        element.setAttribute("limit_min", "0.0");
        element.setAttribute("limit_max", "5.0");
        element.setAttribute("channels", "100");
        element.setAttribute("elevation_min",
                Double.toString(Math.toRadians(30)));
        element.setAttribute("elevation_max",
                Double.toString(Math.toRadians(50)));
        element.setAttribute("azimuth_min", Double.toString(Math.toRadians(0)));
        element.setAttribute("azimuth_max",
                Double.toString(Math.toRadians(180)));

        return element;
    }



    @Test
    public void testPHOTON_SPECTRUM() throws IOException, EPQException {
        Element element = createPhotonSpectrumDetector("det1");

        DetectorExtractor extractor = DetectorExtractorFactory.PHOTON_SPECTRUM;
        assertTrue(extractor.canExtract(element));

        Detector det = extractor.extract(element);
        ChannelDetector chDet = (ChannelDetector) det;
        assertEquals(0.0, chDet.getMinimumLimit(), 1e-4);
        assertEquals(5.0, chDet.getMaximumLimit(), 1e-4);
        assertEquals(100, chDet.getChannels());
        assertEquals(0.05, chDet.getChannelWidth(), 1e-4);

        PhotonDetector phDet = (PhotonDetector) det;
        assertEquals(Math.toRadians(40.0), phDet.getTakeOffAngle(), 1e-4);
        assertEquals(Math.toRadians(90.0), phDet.getAzimuthAngle(), 1e-4);
    }
}
