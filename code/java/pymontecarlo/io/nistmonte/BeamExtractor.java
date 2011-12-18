package pymontecarlo.io.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.ElectronGun;

import java.io.IOException;

import org.jdom.Element;

/**
 * Extractor for the beam implementation.
 * 
 * @author ppinard
 */
public interface BeamExtractor extends Extractor {

    /**
     * Extracts the electron beam from a XML element.
     * 
     * @param beamImplElement
     *            XML element
     * @return electron beam
     * @throws IOException
     *             if an error occurs while reading the options
     * @throws EPQException
     *             if an error occurs while setting up the beam
     */
    public ElectronGun extract(Element beamImplElement) throws IOException,
            EPQException;

}
