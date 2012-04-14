package pymontecarlo.program.nistmonte.input;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.EPQLibrary.FromSI;
import gov.nist.microanalysis.EPQLibrary.ISpectrumData;
import gov.nist.microanalysis.EPQLibrary.SpectrumProperties;
import gov.nist.microanalysis.EPQLibrary.Detector.EDSDetector;
import gov.nist.microanalysis.EPQTools.WriteSpectrumAsEMSA1_0;
import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.GaussianFWHMBeam;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.Properties;
import java.util.zip.ZipOutputStream;

import pymontecarlo.util.ZipUtil;

/**
 * Detector for a photon spectrum.
 * 
 * @author ppinard
 */
public class PhotonSpectrumDetector extends PhotonDetector implements
        ChannelDetector {

    /** Detector storing the photon spectrum. */
    private final EDSDetector detector;



    /**
     * Creates a detector.
     * 
     * @param min
     *            lower energy limit of the detector (in eV)
     * @param max
     *            upper energy limit of the detector (in eV)
     * @param channels
     *            number of channels (bins)
     * @param detectorPosition
     *            position of the detector
     * @return detector
     */
    private static EDSDetector createDetector(double min, double max,
            int channels, double[] detectorPosition) {
        double channelWidth = (max - min) / channels;
        try {
            return EDSDetector.createPerfectDetector(channels, channelWidth,
                    detectorPosition);
        } catch (EPQException e) {
            throw new IllegalArgumentException(e);
        }
    }



    /**
     * Creates a new <code>PhotonSpectrumDetector</code>.
     * 
     * @param takeOffAngle
     *            elevation from the x-y plane (in radians)
     * @param azimuthAngle
     *            counter-clockwise angle from the positive x-axis in the x-y
     *            plane (in radians)
     * @param min
     *            lower energy limit of the detector (in eV)
     * @param max
     *            upper energy limit of the detector (in eV)
     * @param channels
     *            number of channels (bins)
     */
    public PhotonSpectrumDetector(double takeOffAngle, double azimuthAngle,
            double min, double max, int channels) {
        super(takeOffAngle, azimuthAngle);
        detector = createDetector(min, max, channels, getDetectorPosition());
    }



    /**
     * Creates a new <code>PhotonSpectrumDetector</code>.
     * 
     * @param position
     *            detector position in the chamber (in meters)
     * @param min
     *            lower energy limit of the detector (in eV)
     * @param max
     *            upper energy limit of the detector (in eV)
     * @param channels
     *            number of channels (bins)
     */
    public PhotonSpectrumDetector(double[] position, double min, double max,
            int channels) {
        super(position);
        detector = createDetector(min, max, channels, getDetectorPosition());
    }



    @Override
    public void saveResults(ZipOutputStream zipOutput, String key)
            throws IOException {
        // Create EMSA
        ByteArrayOutputStream ostream = new ByteArrayOutputStream();

        ISpectrumData spectrum = detector.getSpectrum(1.0);

        try {
            WriteSpectrumAsEMSA1_0.write(spectrum, ostream,
                    WriteSpectrumAsEMSA1_0.Mode.COMPATIBLE);
        } catch (EPQException e) {
            throw new IOException(e);
        }

        // Save EMSA in ZIP
        ZipUtil.saveByteArray(zipOutput, key + ".emsa", ostream.toByteArray());
    }



    @Override
    public void setup(MonteCarloSS mcss, XRayEventListener2 xrel,
            BremsstrahlungEventListener bel) throws EPQException {
        // Setup properties
        SpectrumProperties props = detector.getSpectrum().getProperties();
        props.setDetectorPosition(getTakeOffAngle(), getAzimuthAngle(),
                0.999 * MonteCarloSS.ChamberRadius, 0.0);
        props.setNumericProperty(SpectrumProperties.BeamEnergy,
                FromSI.keV(mcss.getBeamEnergy()));

        if (mcss.getElectronGun() instanceof GaussianFWHMBeam)
            props.setNumericProperty(SpectrumProperties.ProbeArea, FromSI
                    .nanometer(((GaussianFWHMBeam) mcss.getElectronGun())
                            .getDiameter()));

        // Register action listeners
        xrel.addActionListener(detector);
        bel.addActionListener(detector);
    }



    @Override
    public void reset() {
        super.reset();
        detector.reset();
    }



    @Override
    protected void saveAsProperties(Properties props) {
        super.saveAsProperties(props);

        props.setProperty("histogram.min", Double.toString(getMinimumLimit()));
        props.setProperty("histogram.max", Double.toString(getMaximumLimit()));
        props.setProperty("histogram.channels", Integer.toString(getChannels()));
    }



    @Override
    public double getMinimumLimit() {
        return detector.minEnergyForChannel(0);
    }



    @Override
    public double getMaximumLimit() {
        return detector.maxEnergyForChannel(detector.getChannelCount() - 1);
    }



    @Override
    public int getChannels() {
        return detector.getChannelCount();
    }



    @Override
    public double getChannelWidth() {
        return detector.getChannelWidth();
    }



    @Override
    public boolean requiresBremsstrahlung() {
        return true;
    }



    @Override
    public String getTag() {
        return "PhotonSpectrumResult";
    }
}
